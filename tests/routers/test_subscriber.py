# mypy: disable-error-code="has-type,no-untyped-def"
import random
import typing

import pytest
from fastapi.testclient import TestClient

from tmo.db.models.tables import Subscriber

pytestmark = [pytest.mark.usefixtures("database")]


@pytest.fixture
def subscriber(database: dict[str, list[dict[str, typing.Any]]]):
    _subscriber = random.choice(database["subscriber"])

    return Subscriber.model_validate(_subscriber)


@pytest.fixture
def details(subscriber: Subscriber, database: dict[str, list[dict[str, typing.Any]]]):
    details = [
        {key: value for key, value in detail.items() if not key.endswith("_id")}
        for detail in database["detail"]
        if detail["subscriber_id"] == subscriber.id
    ]
    details.sort(key=lambda k: k["id"])

    return details


def test_get_subscribers(client: TestClient, database: dict[str, list[dict[str, typing.Any]]]):
    response = client.get("/api/subscriber")
    assert response.status_code == 200
    assert len(response.json()) == len(database["subscriber"])
    assert response.json() == sorted(response.json(), key=lambda k: k["id"])


def test_get_subscriber(client: TestClient, subscriber: Subscriber, details: list[dict[str, int | float]]):
    response = client.get(f"/api/subscriber/{subscriber.id}")
    assert response.status_code == 200

    json = subscriber.model_dump(mode="json")

    data = {key: value for key, value in response.json().items() if key != "details"}

    assert json == data
    assert details == response.json()["details"]
