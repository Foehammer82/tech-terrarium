import functools
from uuid import uuid4

from fastapi import FastAPI

from audit_v2 import auditor
from models import Foo

app = FastAPI()
auditor.initialize_middleware(
    app,
    request_audit_topic="requests",
    response_audit_topic="responses",
)


@app.get("/foo")
def read_root(bar: str, baz: int) -> Foo:
    return Foo(some_uuid=uuid4(), bar=bar, baz=baz)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
