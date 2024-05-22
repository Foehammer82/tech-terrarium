from uuid import uuid4

from fastapi import FastAPI

from audit import AuditMiddleware
from models import Foo

app = FastAPI()
app.add_middleware(AuditMiddleware)


@app.get("/foo")
def read_root(bar: str, baz: int) -> Foo:
    return Foo(some_uuid=uuid4(), bar=bar, baz=baz)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
