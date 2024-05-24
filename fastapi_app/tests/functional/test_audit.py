from uuid import uuid4, UUID

import pytest
from pydantic import Field

from src.audit import AuditBaseModel, Auditor


@pytest.fixture(scope="session")
def auditor() -> Auditor:
    return Auditor(
        kafka_brokers="localhost:9092",
        schema_registry_url="http://localhost:8081",
        dead_letter_topic="dead-letter",
    )


@pytest.fixture
def example_user_model(faker) -> AuditBaseModel:
    class ExampleModel(AuditBaseModel):
        uuid: UUID = Field(default_factory=uuid4)
        name: str = Field(default_factory=faker.name)
        address: str = Field(default_factory=faker.address)

    return ExampleModel()


def test_example(auditor, example_user_model):
    """
    NOTES:
      This test requires the kafka containers to be up and running to work properly.  and be available on localhost

      In practice, we want to be able to call the do_audit method and then let it take on the auditing process and
      let us get back to the task at hand ASAP.  one thing to note, we will likely want to implement retry and
      dead-letter topics, so we have a place to push messages that failed for whatever reason.

    :param auditor: Instantiated instance of the Auditor class provided by a pytest fixture
    :param example_user_model: An example user model provided by a pytest fixture
    """

    auditor.audit(audit_data=example_user_model, kafka_topic="test-topic-1")
