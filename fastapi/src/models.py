from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Foo(BaseModel):
    some_uuid: UUID = Field(default_factory=uuid4)
    bar: str = "bar"
    baz: int = 42
