# mypy: disable-error-code="has-type,no-untyped-def"
import random

import pytest
from fastapi.testclient import TestClient

from tmo.db.models.tables import Subscriber

pytestmark = [pytest.mark.usefixtures("database")]


@pytest.fixture
def subscriber(database: dict[str, list[tuple[str, ...]]]):
    id, number, name, format, count = random.choice(database["subscriber"])
    return Subscriber.model_validate(dict(id=id, number=number, name=name, number_format=format, count=count))


def test_get_subscribers(client: TestClient):
    response = client.get("/api/subscriber")
    assert response.status_code == 200
    assert len(response.json()) == 11


def test_get_subscriber(client: TestClient, subscriber: Subscriber):
    breakpoint()
    response = client.get(f"/api/subscriber/{subscriber.id}")
    assert response.status_code == 200 == subscriber
