import threading
from typing import Dict, Tuple
from uuid import UUID, uuid4

import py_avro_schema
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from pydantic import BaseModel, Field
from starlette.types import ASGIApp, Scope, Receive, Send, Message


class AuditMiddleware:
    # noinspection PyUnresolvedReferences
    """
    Middleware for auditing requests and responses.

    This middleware logs the processing time of each request and response,
    and adds it as a custom header to the response.

    Examples:
        >>> from fastapi import FastAPI
        ... from audit import AuditMiddleware
        ...
        ... app = FastAPI()
        ... app.add_middleware(
        ...     AuditMiddleware,
        ...     kafka_brokers="localhost:9092",
        ...     schema_registry_url="http://localhost:8081",
        ...     request_audit_topic="request-audit",
        ...     response_audit_topic="response-audit",
        ... )
    """

    class AuditRequest(BaseModel):
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

    class AuditResponse(BaseModel):
        """Audit response model."""

        request_uuid: UUID
        body: str
        headers: Dict[str, str]
        status_code: int

    def __init__(
        self,
        app: ASGIApp,
        request_audit_topic: str,
        response_audit_topic: str,
        kafka_brokers: str | list[str],
        schema_registry_url: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Initialize the middleware with the given ASGI application.

        Args:
            app: The ASGI application to wrap.
            kafka_brokers: The Kafka broker(s) to connect to.
            schema_registry_url: The URL of the Kafka schema registry.
            request_audit_topic: The Kafka topic to send request audits to.
            response_audit_topic: The Kafka topic to send response audits to.
            disabled: Whether to disable the middleware.
        """
        self._app = app
        self._disabled = disabled
        self._request_audit_topic = request_audit_topic
        self._request_schema = avro.loads(py_avro_schema.generate(self.AuditRequest))
        self._response_audit_topic = response_audit_topic
        self._response_schema = avro.loads(py_avro_schema.generate(self.AuditResponse))

        # TODO: testing out using a single producer and topic for both request and response audits.  will need to see
        #       if it works as expected with the schema registry
        self._kafka_producer = AvroProducer(
            config={
                "bootstrap.servers": kafka_brokers,
                "schema.registry.url": schema_registry_url,
            }
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process each request and response.

        This method is called for every request. It starts an audit thread for the request,
        processes the request, and then starts an audit thread for the response.
        """
        if not self._disabled and scope["type"] == "http":
            scope_cleaned = {
                key: value for key, value in scope.items() if key != "headers"
            }
            scope_cleaned["headers"] = [
                (key.decode(), value.decode()) for key, value in scope["headers"]
            ]

            request = self.AuditRequest.model_validate(scope_cleaned)
            audit_request_thread = threading.Thread(
                target=self._do_request_audit, args=[request]
            )
            audit_request_thread.start()

            response_body = b""
            response_status = 200
            response_headers = {}

            async def custom_send(message: Message) -> None:
                """
                Custom send function to collect the response body.
                """
                nonlocal response_body, response_status, response_headers

                if message.get("type") == "http.response.start":
                    response_status = message["status"]
                    response_headers = message.setdefault("headers", [])
                elif message.get("type") == "http.response.body":
                    response_body += message.get("body", b"")
                await send(message)

            # Process the request and response
            await self._app(scope, receive, custom_send)

            # Start a new thread to audit the response
            audit_response_thread = threading.Thread(
                target=self._do_response_audit,
                args=[request.uuid, response_body, response_status, response_headers],
            )
            audit_response_thread.start()

        else:
            await self._app(scope, receive, send)

    def _do_request_audit(self, request: AuditRequest):
        """
        Audit the request.

        This method is intended to be run in a separate thread.
        """

        self._kafka_producer.produce(
            topic=self._request_audit_topic,
            value=request.dict(),
            key_schema=request.avro_schema,
        )
        self._kafka_producer.flush()

    def _do_response_audit(
        self,
        request_uuid: UUID,
        body: bytes,
        status_code: int,
        headers: list[tuple[str, str]],
    ):
        """
        Audit the response.

        This method is intended to be run in a separate thread.
        """

        response = self.AuditResponse(
            request_uuid=request_uuid,
            body=body,
            status_code=status_code,
            headers={header[0]: header[1] for header in headers},
        )
        self._kafka_producer.produce(
            topic=self._response_audit_topic,
            value=response.dict(),
            key_schema=response.avro_schema,
        )
        self._kafka_producer.flush()


if __name__ == "__main__":


    # TODO: move to tests to assert these work
    t1 = avro.loads(py_avro_schema.generate(AuditRequest))
    t2 = avro.loads(py_avro_schema.generate(AuditResponse))

    print("here")
