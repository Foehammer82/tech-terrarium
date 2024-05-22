import sys
from typing import Dict, Any
from uuid import uuid4, UUID

import py_avro_schema
from pydantic import BaseModel, Field, field_validator


class Bar:
    attr_0: str = "bar"

    @classmethod
    def change_attr_0(cls, new_value: str):
        cls.attr_0 = new_value


# shows that the class attribute is shared among all instances
print(Bar().attr_0)
Bar.change_attr_0("baz")
print(Bar().attr_0)


class Foo(BaseModel):
    """Foo dummy model."""

    attr_0: UUID = Field(default_factory=uuid4)
    attr_1: str
    attr_2: int
    attr_3: Dict[str, Any]

    _max_dict_size_bytes = 1 * (10 ^ 6)  # MB

    # noinspection PyNestedDecorators
    @field_validator('attr_3')
    @classmethod
    def avoid_large_dictionaries(cls, v: dict) -> dict:
        size_sys = sys.getsizeof(v)
        print(f"Size of dictionary using sys.getsizeof(): {size_sys} bytes")

        return v


Foo._max_dict_size_bytes = 5 * (10 ** 6)

if __name__ == '__main__':
    schema = py_avro_schema.generate(Foo)
    example_1 = Foo(attr_1="some data", attr_2=3, attr_3={"key": "value"})
    print(example_1._max_dict_size_bytes)

    print(schema)
