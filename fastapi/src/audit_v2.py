# TODO: determine how best to implement auditing into this such that i can audit anywhere i please and only
#       need to call something
import threading
from typing import Dict, Tuple
from uuid import UUID, uuid4

import py_avro_schema
from avro.schema import Schema
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from fastapi import FastAPI
from pydantic import Field, BaseModel
from starlette.requests import Request
from starlette.responses import Response


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


class HttpAuditResponse(BaseModel):
    """Audit response model."""

    request_uuid: UUID
    body: str
    headers: Dict[str, str]
    status_code: int


class Auditor:

    def __init__(
        self,
        kafka_brokers: str | list[str],
        schema_registry_url: str | None = None,
    ):
        self.configs = "my configs"
        self._kafka_producer = AvroProducer(
            config={
                "bootstrap.servers": kafka_brokers,
                "schema.registry.url": schema_registry_url,
            }
        )

    def _do_audit(self, audit_data: BaseModel, kafka_topic: str, avro_schema: Schema):
        # TODO: if anything goes wrong, we need to make sure we handle it properly.  either raising an error or
        #       attempting to send to a retry or dead-letter topic.

        self._kafka_producer.produce(
            topic=kafka_topic,
            value=audit_data.dict(),
            key_schema=avro_schema,
        )
        self._kafka_producer.flush()

    def audit(self, audit_data: BaseModel, kafka_topic: str):
        if not isinstance(audit_data, BaseModel):
            raise ValueError("audit_data must be an instance of pydantic.BaseModel")
        try:
            avro_schema = avro.loads(py_avro_schema.generate(audit_data))
        except Exception as e:
            raise ValueError(f"Error generating Avro schema") from e

        # run the audit in a separate thread, so we can get back to the task at hand ASAP
        audit_request_thread = threading.Thread(
            target=self._do_audit, args=[audit_data, kafka_topic, avro_schema]
        )
        audit_request_thread.start()

        # TODO: make sure everything is being adequately logged (hoping the tooling has built in logging)

    def initialize_middleware(self, app: FastAPI):
        @app.middleware("http")
        async def audit_request_and_response(request: Request, call_next):
            t1 = HttpAuditRequest.model_validate(dict(request))

            response: Response = await call_next(request)


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
