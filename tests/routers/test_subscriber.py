import faker
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.helpers import phone_number
from tmo.db.models.tables import Subscriber


@pytest.fixture(scope="module")
def subscriber(session: Session, client: TestClient):
    subscriber = Subscriber(number=phone_number(), name=faker.Faker().name())
    session.add(subscriber)
    session.commit()

    yield subscriber


def test_get_subscribers(client: TestClient, subscriber: Subscriber):
    response = client.get("/api/subscriber")
    assert response.status_code == 200
    assert len(response.json()) == 1 and response.json() == "1234"
