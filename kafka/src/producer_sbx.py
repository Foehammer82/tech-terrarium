from uuid import uuid4, UUID

import py_avro_schema
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from pydantic import BaseModel, Field


class Foo(BaseModel):
    """Foo dummy model."""

    some_uuid: UUID = Field(default_factory=uuid4)
    bar: str
    baz: int


value_schema = avro.loads(py_avro_schema.generate(Foo))

avroProducer = AvroProducer(
    config={
        "bootstrap.servers": "localhost:9092",
        "schema.registry.url": "http://localhost:8081",
    },
    default_value_schema=value_schema,
)

avroProducer.produce(topic="mytopic", value=Foo(bar="some data", baz=3).dict())
avroProducer.flush()

if __name__ == "__main__":
    pass
