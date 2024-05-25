import abc
import threading
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

import orjson
import py_avro_schema
from confluent_kafka import Producer
from confluent_kafka.avro import SerializerError
from confluent_kafka.schema_registry import SchemaRegistryClient, SchemaRegistryError
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from fastapi import FastAPI
from loguru import logger
from pydantic import Field, BaseModel, model_validator, PrivateAttr
from starlette.concurrency import iterate_in_threadpool
from starlette.requests import Request


# NOTE: we used loguru for ease of use in this code, but to make this more generic you can easily swap it
#       out to base pythong logger by doing the following:
# logger = logging.getLogger("audit")
# logger.setLevel(logging.INFO)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)
# logger.addHandler(console_handler)

# TODO: make it optional to use avro or json serialization and switch to json.
#       - lesson learned: avro may be fast, but is not very flexible and may end up creating more challenges down the
#         road for auditing.  since we end up using json in avro for nested dicts anyway.  Avro is great if for simple
#         data structures, but for more complex data structures, it may be better to just use json.  even with the loss
#         of speed.  it might be nice to use this to build the starlette middleware to use avro and the default
#         auditing to use json, and possibly move away from subclassing BaseModel to AuditBaseModel and just use
#         BaseModel.  then have the BaseModel checked for serialization at start of auditing.


class AuditBaseModel(BaseModel, abc.ABC):
    # TODO: add validation check for no Tuple's or Unions.
    # TODO: review and make sure all types adhere to Avro types
    #       https://avro.apache.org/docs/1.11.1/specification/#primitive-types

    _audit_uuid = PrivateAttr(default_factory=uuid4)
    _avro_schema: str = None

    @property
    def audit_uuid(self):
        """
        The UUID of the audit model.

        Notes:
            We use a property here to ensure that the UUID is not `easily` edited during the object lifecycle. and
            so that the UUID is not passed to the json output of the pydantic model.  This enables it to be used
            programmatically, but not be appended unexpectedly to the json output.
        """
        return self._audit_uuid

    @classmethod
    def get_avro_schema(cls):
        return py_avro_schema.generate(cls).decode()

    def avro_dict(self):
        dict = self.dict()

        if all([type(k) is str for k in dict.items()]):


        return {k: v if (type(v) is Dict[str, Any]) else orjson.dumps(v) for k, v in self.dict().items()}

    @model_validator(mode="before")
    @classmethod
    def check_avro_schema(cls, data: Any) -> Any:
        try:
            cls._avro_schema = py_avro_schema.generate(cls).decode()
        except Exception as e:
            raise ValueError(f"Failed to generate Avro schema for {cls.__name__}: {e}") from e

        return data


class Auditor:
    # TODO: configure a timer or scheduler to reprocess audit messages on the retry-topic
    _kafka_dead_letter_producer: Optional[Producer] = None

    def __init__(
        self,
        kafka_brokers: str | list[str],
        schema_registry_url: str,
        schema_registry_default_models: list[AuditBaseModel] = None,
        retry_topic: str | None = None,
        dead_letter_topic: str | None = None,
    ):
        # store the Avro serializers for the default models in the schema registry
        self._schema_registry_url = schema_registry_url
        self._schema_registry_models: dict[AuditBaseModel.__class__.__name__, AvroSerializer] = (
            {model.__class__.__name__: self._get_avro_serializer(model) for model in schema_registry_default_models}
            if schema_registry_default_models
            else {}
        )

        # Initialize the main Kafka producer
        self._kafka_producer = Producer({"bootstrap.servers": kafka_brokers})

        # Initialize the retry producer if a retry topic is provided
        self._retry_topic = retry_topic
        if retry_topic:
            if self._kafka_producer.list_topics(retry_topic).topics[retry_topic].error:
                raise ValueError(f"Retry topic `{retry_topic}` does not exist!  Create it in Kafka first.")
            self._kafka_retry_producer = Producer({"bootstrap.servers": kafka_brokers})

        # Initialize the dead-letter producer if a dead-letter topic is provided
        self._dead_letter_topic = dead_letter_topic
        if dead_letter_topic:
            if self._kafka_producer.list_topics(dead_letter_topic).topics[dead_letter_topic].error:
                raise ValueError(f"Dead-Letter topic `{dead_letter_topic}` does not exist!  Create it in Kafka first.")
            self._kafka_dead_letter_producer = Producer({"bootstrap.servers": kafka_brokers})
        else:
            logger.warning("No dead-letter topic configured, messages that fail to be delivered will be lost.")

    def add_model_to_schema_registry(self, model: AuditBaseModel):
        if isinstance(model, AuditBaseModel):
            self._schema_registry_models[model.__class__.__name__] = self._get_avro_serializer(model.__class__)
        else:
            self._schema_registry_models[model.__name__] = self._get_avro_serializer(model)

    def audit(self, audit_data: AuditBaseModel, kafka_topic: str):
        logger.debug(f"Current Thread: {threading.current_thread()}")

        if not isinstance(audit_data, AuditBaseModel):
            raise ValueError("audit_data must be an instance of AuditBaseModel")

        # TODO: CONSIDERATION: need to setup some rigorous testing on this to see how it handles being hit heavily from
        #                      async calls (will also want to adapt this to run async as well)  might need to setup a
        #                      queue, or maybe just need to produce asynchrously and let the kafka producer handle the
        #                      rest.  take a look at: https://www.confluent.io/blog/kafka-python-asyncio-integration/
        # run the audit in a separate thread, so we can get back to the task at hand ASAP
        audit_request_thread = threading.Thread(target=self._do_audit, args=[audit_data, kafka_topic])
        audit_request_thread.start()

    def _do_audit(self, audit_data: AuditBaseModel, kafka_topic: str):
        logger.info(f"Auditing {audit_data} to {kafka_topic}")
        logger.debug(f"Current Thread: {threading.current_thread()}")

        # If the model is in the schema registry, we can just grab the schema from there, otherwise we need to generate
        # the schema and store it in the registry
        if not isinstance(audit_data, AuditBaseModel):
            raise ValueError("audit_data must be an instance of AuditBaseModel")

        if audit_data.__class__.__name__ in self._schema_registry_models:
            avro_serializer = self._schema_registry_models[audit_data.__class__.__name__]
        else:
            avro_serializer = self._get_avro_serializer(audit_data)
            self._schema_registry_models[audit_data.__class__.__name__] = avro_serializer

        try:
            avro_value = avro_serializer(audit_data.avro_dict(), SerializationContext(kafka_topic, MessageField.VALUE))
        except SchemaRegistryError as e:
            self._produce_to_dead_letter_topic(audit_data.model_dump_json(), str(audit_data.audit_uuid))
            raise ValueError(
                f"Failed registering audit_uuid `{audit_data.audit_uuid}` to the Schema Registry!\n"
                "HINT: you may need to go and delete the currently registered schema, though note that this may have "
                "unintended consequences as any existing topic data may not be able to be serialized using the new "
                "schema.  In short, you either expected (or are not surprised by this error) and likely want to delete "
                "the existing registry, OR, you are surprised by this error and likely want to investigate further.\n"
                f"SchemaRegistryError: {e}"
            ) from e
        except SerializerError as e:
            self._produce_to_dead_letter_topic(audit_data.model_dump_json(), str(audit_data.audit_uuid))
            raise ValueError(f"Failed to serialize audit data `{audit_data}` to Avro!\nSerializerError: {e}") from e

        # TODO: review the docs and make sure we are handling .flush() correctly and whether we need to perform
        #       different actions in case of exceptions to keep things running smoothly.  It might be idea to figure
        #       out how to run everything on one producer and just properly handle flushing or purging the producer.
        try:
            self._kafka_producer.produce(
                topic=kafka_topic,
                value=avro_value,
                key=str(audit_data.audit_uuid),
                on_delivery=self._delivery_report,
            )
        except Exception as e:
            self._produce_to_retry_topic(audit_data.model_dump_json(), str(audit_data.audit_uuid))
            raise ValueError(f"Failed to produce audit data `{audit_data}` to Kafka!\nException: {e}") from e
        finally:
            self._kafka_producer.flush()

    def _get_avro_serializer(self, model: AuditBaseModel) -> Optional[AvroSerializer]:
        """Generate an Avro serializer for the provided model."""
        logger.debug(f"Current Thread: {threading.current_thread()}")

        return (
            AvroSerializer(
                schema_registry_client=SchemaRegistryClient(
                    conf={"url": self._schema_registry_url},
                ),
                schema_str=model.get_avro_schema(),
            )
            if self._schema_registry_url
            else None
        )

    def _produce_to_retry_topic(self, value: str, key: str | None = None):
        """
        Produces a message to the retry topic.

        Args:
            value (str): The value of the message to produce.
            key (str): The key of the message to produce.
        """
        logger.debug(f"Current Thread: {threading.current_thread()}")

        if self._retry_topic:
            self._kafka_retry_producer.produce(
                topic=self._retry_topic,
                value=value,
                key=key,
                on_delivery=self._delivery_report,
            )
            self._kafka_retry_producer.flush()
        else:
            logger.warning(f"No retry topic configured, forward to the dead-letter topic.")
            self._produce_to_dead_letter_topic(value, key)

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
        logger.debug(f"Current Thread: {threading.current_thread()}")

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
            f"record {msg.key().decode() + ' ' if msg.key() else ''}successfully produced to "
            f"{msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )

    def _produce_to_dead_letter_topic(self, value: str, key: str | None = None):
        """
        Produces a message to the dead-letter topic.

        Args:
            value (str): The value of the message to produce.
            key (str): The key of the message to produce.
        """
        logger.debug(f"Current Thread: {threading.current_thread()}")

        if self._dead_letter_topic:
            self._kafka_dead_letter_producer.produce(
                topic=self._dead_letter_topic,
                value=value,
                key=key,
                on_delivery=self._break_glass,
            )
            self._kafka_dead_letter_producer.flush()
        else:
            logger.warning(f"No dead-letter topic configured, message {key} will be lost: {value}")

    @staticmethod
    def _break_glass(err, msg):
        """This is a callback that will raise an exception if a message fails to be delivered."""
        # TODO: make sure this halts the program and doesn't just log the error (if running in a separate thread)
        logger.debug(f"Current Thread: {threading.current_thread()}")

        if err is not None:
            raise Exception(f"A message failed to be delivered to the dead-letter topic: {err}")


class HttpAuditRequest(AuditBaseModel):
    """Audit request model."""

    uuid: UUID = Field(default_factory=uuid4)
    type: str
    asgi: Dict[str, str]
    http_version: str
    client: str
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
        request_dict["client"] = f"{request.client.host}:{request.client.port}"
        return cls(**request_dict)


class HttpAuditResponse(AuditBaseModel):
    """Audit response model."""

    request_uuid: UUID
    body: Dict[str, Any]
    headers: Dict[str, str]
    status_code: int


def initialize_starlette_middleware(
    app: FastAPI,
    auditor: Auditor,
    request_audit_topic: str,
    response_audit_topic: str,
):
    # Generate the Avro schemas for the audit models and store them in the schema registry
    auditor.add_model_to_schema_registry(HttpAuditRequest)
    auditor.add_model_to_schema_registry(HttpAuditResponse)

    # Add middleware to the FastAPI app to audit requests and responses
    @app.middleware("http")
    async def audit_request_and_response(request: Request, call_next):
        audit_request_model = HttpAuditRequest.from_request(request)
        auditor.audit(
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
            response_body = None

        auditor.audit(
            audit_data=HttpAuditResponse(
                request_uuid=audit_request_model.uuid,
                body=response_body,
                headers=response_headers,
                status_code=response.status_code,
            ),
            kafka_topic=response_audit_topic,
        )

        return response
