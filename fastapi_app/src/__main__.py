from uuid import uuid4

from fastapi import FastAPI

from audit import Auditor, initialize_starlette_middleware
from models import Foo

auditor = Auditor(
    kafka_brokers="localhost:9092",
    schema_registry_url="http://localhost:8081",
    dead_letter_topic="dead-letter",
)

app = FastAPI()
initialize_starlette_middleware(
    app,
    auditor=auditor,
    request_audit_topic="fastapi-requests",
    response_audit_topic="fastapi-responses",
)


@app.get("/foo")
def read_root(bar: str, baz: int) -> Foo:
    return Foo(some_uuid=uuid4(), bar=bar, baz=baz)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
