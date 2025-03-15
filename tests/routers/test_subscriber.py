# mypy: disable-error-code="has-type,no-untyped-def"
import contextlib
import secrets
import typing

import pytest
from fastapi.testclient import TestClient

from tmo.db.models.tables import Detail, Subscriber
from tmo.web.routers.models.get import ReadSubscriberDetail

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.fixture
def details(subscriber: Subscriber, database_values: dict[str, list[dict[str, typing.Any]]]):
    details = [
        {key: value for key, value in detail.items() if not key.endswith("_id")}
        for detail in database_values["detail"]
        if detail["subscriber_id"] == subscriber.id
    ]
    details.sort(key=lambda k: k["id"])

    return details


@pytest.mark.parametrize(
    ("count", "cm"),
    (
        (slice(1), contextlib.nullcontext()),
        (slice(-1), pytest.raises(ValueError, match="Data must only contain one detail entry")),
    ),
    ids=("one", "all"),
)
def test_model_validate(
    count: slice, cm: typing.ContextManager[None], subscriber: Subscriber, details: list[dict[str, int | float]]
):
    _details = [Detail(**detail) for detail in details]

    with cm:
        ReadSubscriberDetail.model_validate({**subscriber.model_dump(mode="json"), "details": _details[count]})


@pytest.mark.parametrize("count", (5, -1), ids=("paginated", "default"))
def test_get_subscribers(count: int, client: TestClient):
    if count < 0:
        response = client.get("/api/subscriber")
        count = 10
    else:
        response = client.get("/api/subscriber", params={"count": count})

    assert response.status_code == 200
    assert len(response.json()) == count
    assert response.json() == sorted(response.json(), key=lambda k: k["id"])


def test_get_subscriber(client: TestClient, subscriber: Subscriber, details: list[dict[str, int | float]]):
    response = client.get(f"/api/subscriber/{subscriber.id}")
    assert response.status_code == 200

    json = subscriber.model_dump(mode="json")

    data = {key: value for key, value in response.json().items() if key != "details"}

    assert json == data
    assert details == response.json()["details"]


def test_get_subscriber_missing(client: TestClient, database_values: dict[str, list[dict[str, typing.Any]]]):
    id = len(database_values["subscriber"]) + 1

    response = client.get(f"/api/subscriber/{id}")
    assert response.status_code == 404


@pytest.mark.parametrize("state", (-1, 0, 1), ids=("exists", "invalid number", "success"))
def test_post_subscriber(state: int, client: TestClient, subscriber: Subscriber):
    if state == -1:
        response = client.post("/api/subscriber", json={"name": secrets.token_hex(), "number": subscriber.number})
        assert response.status_code == 409 and response.json() == {
            "detail": f"A subscriber with the number {subscriber.number} already exists (ID={subscriber.id})"
        }

    if state == 0:
        response = client.post("/api/subscriber", json={"name": secrets.token_hex(16), "number": secrets.token_hex(16)})
        assert response.status_code == 422

    if state == 1:
        response = client.post(
            "/api/subscriber", json={"name": (name := secrets.token_hex()), "number": (number := secrets.token_hex(4))}
        )
        id = response.json()["id"]

        assert response.status_code == 200 and response.json() == {
            "name": name,
            "number": number,
            "format": "us",
            "id": id,
        }
