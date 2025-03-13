import secrets
import typing

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def bill_id(client: TestClient) -> int:
    response = client.post("/api/bill", json={"date": "2000-01-01"})
    assert response.status_code == 200
    return typing.cast(int, response.json()["id"])


@pytest.fixture(scope="module")
def subscriber_id(client: TestClient) -> int:
    response = client.post("/api/subscriber", json={"name": secrets.token_hex(), "number": secrets.token_hex(4)})
    assert response.status_code == 200
    return typing.cast(int, response.json()["id"])
