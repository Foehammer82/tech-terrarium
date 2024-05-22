from uuid import UUID

from pydantic import BaseModel


class Foo(BaseModel):
    some_uuid: UUID
    bar: str
    baz: int
