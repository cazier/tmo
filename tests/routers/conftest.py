import itertools
import secrets
import typing

import pytest
from fastapi.testclient import TestClient

bill_counter = itertools.count(2100)


@pytest.fixture
def bill_id(request: pytest.FixtureRequest, client: TestClient) -> tuple[int, bool]:
    if request.param:
        response = client.post("/api/bill", json={"date": f"{next(bill_counter)}-01-01"})
        assert response.status_code == 200
        id = typing.cast(int, response.json()["id"])

    else:
        response = client.get("/api/bill", params={"count": 100})
        assert response.status_code == 200
        id = typing.cast(int, max(bill["id"] for bill in response.json())) + 1

    return id, request.param


@pytest.fixture
def subscriber_id(request: pytest.FixtureRequest, client: TestClient) -> tuple[int, bool]:
    if request.param:
        response = client.post("/api/subscriber", json={"name": secrets.token_hex(), "number": secrets.token_hex(4)})
        assert response.status_code == 200
        id = typing.cast(int, response.json()["id"])
    else:
        response = client.get("/api/subscriber", params={"count": 100})
        assert response.status_code == 200
        id = typing.cast(int, max(subscriber["id"] for subscriber in response.json())) + 1

    return id, request.param
