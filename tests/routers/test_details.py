# INSERT INTO detail ("id", "bill_id", "subscriber_id", "phone", "line", "insurance", "usage", "total", "minutes", "messages", "data") VALUES(  1,  1,  1, 13.65, 26.25, 11.61, 20.27,  71.78, 180, 838, 14.709);

# mypy: disable-error-code="has-type,no-untyped-def"
import secrets

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


def test_post_details(
    client: TestClient,
):
    response = client.post("/api/bill", json={"date": "2000-01-01"})
    assert response.status_code == 200
    bill_id = response.json()["id"]

    response = client.post("/api/subscriber", json={"name": secrets.token_hex(), "number": secrets.token_hex(4)})
    assert response.status_code == 200
    subscriber_id = response.json()["id"]

    detail = {
        "phone": 1.0,
        "line": 2.0,
        "insurance": 3.0,
        "usage": 4.0,
        "minutes": 5,
        "messages": 6,
        "data": 7,
    }

    response = client.post("/api/detail", params={"bill": bill_id, "subscriber": subscriber_id}, json=detail)
    assert response.status_code == 200 and response.json() == {
        **detail,
        "total": 10.0,
        "bill_id": bill_id,
        "subscriber_id": subscriber_id,
    }
