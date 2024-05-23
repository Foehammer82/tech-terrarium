# TODO: determine how best to implement auditing into this such that i can audit anywhere i please and only
#       need to call something
import threading
from typing import Dict, Tuple, Any, Union
from uuid import UUID, uuid4

import orjson
import py_avro_schema
from avro.schema import Schema
from confluent_kafka import avro, Producer
from confluent_kafka.avro import AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from fastapi import FastAPI
from pydantic import Field, BaseModel
from starlette.concurrency import iterate_in_threadpool
from starlette.requests import Request


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
        request_dict["headers"] = {
            h[0].decode(): h[1].decode() for h in request.headers.raw
        }
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
    ):
        self._schema_registry_url = schema_registry_url
        self._kafka_producer_2 = Producer(config={"bootstrap.servers": kafka_brokers})

        self._kafka_producer = AvroProducer(
            config={
                "bootstrap.servers": kafka_brokers,
                "schema.registry.url": schema_registry_url,
            }
        )

    def _do_audit(self, audit_data: BaseModel, kafka_topic: str, avro_schema: Schema):
        # TODO: if anything goes wrong, we need to make sure we handle it properly.  either raising an error or
        #       attempting to send to a retry or dead-letter topic.

        avro_serializer = AvroSerializer(
            schema_registry_client=SchemaRegistryClient(
                conf={"url": self._schema_registry_url},
            ),
            schema_str=avro_schema,
        )

        self._kafka_producer.produce(
            topic=kafka_topic,
            value=audit_data.dict(),
            value_schema=avro_schema,
        )
        self._kafka_producer.flush()

    def audit(self, audit_data: BaseModel, kafka_topic: str):
        if not isinstance(audit_data, BaseModel):
            raise ValueError("audit_data must be an instance of pydantic.BaseModel")
        try:
            avro_schema = avro.loads(py_avro_schema.generate(audit_data.__class__))
        except Exception as e:
            raise ValueError(f"Error generating Avro schema") from e

        # run the audit in a separate thread, so we can get back to the task at hand ASAP
        audit_request_thread = threading.Thread(
            target=self._do_audit, args=[audit_data, kafka_topic, avro_schema]
        )
        audit_request_thread.start()

        # TODO: make sure everything is being adequately logged (hoping the tooling has built in logging)

    def initialize_middleware(
        self,
        app: FastAPI,
        request_audit_topic: str,
        response_audit_topic: str,
        only_audit_json_responses: bool = True,
    ):
        @app.middleware("http")
        async def audit_request_and_response(request: Request, call_next):
            audit_request_model = HttpAuditRequest.from_request(request)
            self.audit(
                audit_data=audit_request_model,
                kafka_topic=request_audit_topic,
            )

            response = await call_next(request)

            # get the response headers as a dict of strings
            response_headers = {
                h[0].decode(): h[1].decode() for h in response.headers.raw
            }

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


# Below is the code that would be in the main file that we want to audit #
# We want to have a single instance of the Auditor class that we can use anywhere in our codebase.
auditor = Auditor(
    kafka_brokers="localhost:9092",
    schema_registry_url="http://localhost:8081",
)


class Foo(BaseModel):
    attr_01: UUID = Field(default_factory=uuid4)
    attr_02: str = "test_string"
    attr_03: int = 123


def do_a_thing():

    foo = Foo()

    # In practice, we want to be able to call the do_audit method and then let it take on the auditing process and
    # let us get back to the task at hand ASAP.  one thing to note, we will likely want to implement retry and
    # dead-letter topics, so we have a place to push messages that failed for whatever reason.
    auditor.audit(audit_data=foo, kafka_topic="test-topic-1")

    return "I did a thing"


if __name__ == "__main__":
    do_a_thing()
    print("\ndone doing a thing")
