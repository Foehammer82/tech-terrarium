# TODO: determine how best to implement auditing into this such that i can audit anywhere i please and only
#       need to call something
import logging
import threading
from typing import Dict, Tuple, Any, Union
from uuid import UUID, uuid4

import orjson
import py_avro_schema
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from fastapi import FastAPI
from pydantic import Field, BaseModel
from starlette.concurrency import iterate_in_threadpool
from starlette.requests import Request

logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

# create console handler and set level to info
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


class HttpAuditRequest(BaseModel):
    """Audit request model."""

    uuid: UUID = Field(default_factory=uuid4)
    type: str
    asgi: Dict[str, str]
    http_version: str
    server: Tuple[str, int]
    client: Tuple[str, int]
    scheme: str
    root_path: str
    headers: Dict[str, str]
    method: str
    path: str
    query_string: str

    @classmethod
    def from_request(cls, request: Request) -> "HttpAuditRequest":
        request_dict = dict(request)
        request_dict["headers"] = {h[0].decode(): h[1].decode() for h in request.headers.raw}
        return cls(**request_dict)


class HttpAuditResponse(BaseModel):
    """Audit response model."""

    request_uuid: UUID
    body: Union[Dict[str, Any], str]
    headers: Dict[str, str]
    status_code: int


class Auditor:
    def __init__(
        self,
        kafka_brokers: str | list[str],
        schema_registry_url: str | None = None,
        schema_registry_default_models: list[BaseModel] = None,
        dead_letter_topic: str | None = None,
    ):
        self._dead_letter_topic = dead_letter_topic
        self._schema_registry_url = schema_registry_url
        self.schema_registry_models: dict[BaseModel.__class__, AvroSerializer] = (
            {model.__class__: self._get_avro_serializer(model) for model in schema_registry_default_models}
            if schema_registry_default_models
            else {}
        )
        self._kafka_producer = Producer({"bootstrap.servers": kafka_brokers})

    def initialize_middleware(
        self,
        app: FastAPI,
        request_audit_topic: str,
        response_audit_topic: str,
        only_audit_json_responses: bool = True,
    ):
        # Generate the Avro schemas for the audit models and store them in the schema registry
        self.schema_registry_models[HttpAuditRequest.__class__] = self._get_avro_serializer(HttpAuditRequest)
        self.schema_registry_models[HttpAuditResponse.__class__] = self._get_avro_serializer(HttpAuditResponse)

        # Add middleware to the FastAPI app to audit requests and responses
        @app.middleware("http")
        async def audit_request_and_response(request: Request, call_next):
            audit_request_model = HttpAuditRequest.from_request(request)
            self.audit(
                audit_data=audit_request_model,
                kafka_topic=request_audit_topic,
            )

            response = await call_next(request)

            # get the response headers as a dict of strings
            response_headers = {h[0].decode(): h[1].decode() for h in response.headers.raw}

            # Obtain the response body as a dictionary of strings
            response_body_bytes = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body_bytes))
            if response_headers.get("content-type", None) == "application/json":
                response_body = orjson.loads(b"".join(response_body_bytes))
            else:
                response_body = b"".join(response_body_bytes).decode()

            # self.audit(
            #     audit_data=HttpAuditResponse(
            #         request_uuid=audit_request_model.uuid,
            #         body=response_body,
            #         headers=response_headers,
            #         status_code=response.status_code,
            #     ),
            #     kafka_topic=response_audit_topic,
            # )

            return response

    def audit(self, audit_data: BaseModel, kafka_topic: str):
        logger.debug(f"Current Thread: {threading.current_thread()}")

        if not isinstance(audit_data, BaseModel):
            raise ValueError("audit_data must be an instance of pydantic.BaseModel")

        # run the audit in a separate thread, so we can get back to the task at hand ASAP
        audit_request_thread = threading.Thread(target=self._do_audit, args=[audit_data, kafka_topic])
        audit_request_thread.start()

    def _do_audit(self, audit_data: BaseModel, kafka_topic: str):
        logger.info(f"Auditing {audit_data} to {kafka_topic}")
        logger.debug(f"Current Thread: {threading.current_thread()}")

        # If the model is in the schema registry, we can just grab the schema from there
        if audit_data.__class__ in self.schema_registry_models:
            avro_serializer = self.schema_registry_models[audit_data.__class__]

        # If the model is not in the schema registry, we need to generate the schema and store it in the registry
        else:
            avro_serializer = self._get_avro_serializer(audit_data)
            self.schema_registry_models[audit_data.__class__] = avro_serializer

        # TODO: read this and think through how to set the key:
        #       https://forum.confluent.io/t/what-should-i-use-as-the-key-for-my-kafka-message/312
        # TODO: consider adding the on_delivery callback to the produce method
        self._kafka_producer.produce(
            topic=kafka_topic,
            value=avro_serializer(audit_data.dict(), SerializationContext(kafka_topic, MessageField.VALUE)),
            on_delivery=self._delivery_report,
        )
        self._kafka_producer.flush()

    def _get_avro_serializer(self, model: BaseModel):
        # TODO: would be cleaner to make a subclassed BaseModel with a validator the checks the avro schema can
        #       be generated and stores it in the model for use.  this way it can fail when the model is defined long
        #       before it ever gets to the auditor and avoid unnecessary errors in the auditor.
        avro_schema_str = py_avro_schema.generate(model.__class__).decode()

        return AvroSerializer(
            schema_registry_client=SchemaRegistryClient(
                conf={"url": self._schema_registry_url},
            ),
            schema_str=avro_schema_str,
        )

    def _delivery_report(self, err, msg):
        """
        Reports the failure or success of a message delivery.

        Args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.

        Note:
            In the delivery report callback the Message.key() and Message.value()
            will be the binary format as encoded by any configured Serializers and
            not the same object that was passed to produce().
            If you wish to pass the original object(s) for key and value to delivery
            report callback we recommend a bound callback or lambda where you pass
            the objects along.
        """

        if err is not None:
            logger.error(f"Delivery failed for record {msg.key()}: {err}")

            if self._dead_letter_topic:
                self._kafka_producer.produce(
                    topic=self._dead_letter_topic,
                    value=msg.value(),
                    key=msg.key(),
                    on_delivery=self._break_glass,
                )
                self._kafka_producer.flush()

            return
        logger.info(
            f"record {msg.key() + ' ' if msg.key() else ''}successfully produced to "
            f"{msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )

    @staticmethod
    def _break_glass(err, msg):
        """This is a callback that will raise an exception if a message fails to be delivered."""
        if err is not None:
            raise Exception(f"A message failed to be delivered to the dead-letter topic: {err}")


# Below is the code that would be in the main file that we want to audit #
# We want to have a single instance of the Auditor class that we can use anywhere in our codebase.
auditor = Auditor(
    kafka_brokers="localhost:9092",
    schema_registry_url="http://localhost:8081",
    dead_letter_topic="dead-letter",
)


class Foo(BaseModel):
    attr_01: UUID = Field(default_factory=uuid4)
    attr_02: str = "test_string"
    attr_03: int = 123


if __name__ == "__main__":
    foo = Foo()

    # In practice, we want to be able to call the do_audit method and then let it take on the auditing process and
    # let us get back to the task at hand ASAP.  one thing to note, we will likely want to implement retry and
    # dead-letter topics, so we have a place to push messages that failed for whatever reason.
    auditor.audit(audit_data=foo, kafka_topic="test-topic-1")
    logger.info("done auditing foo")
