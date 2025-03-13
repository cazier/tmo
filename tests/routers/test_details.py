# mypy: disable-error-code="has-type,no-untyped-def"

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


def test_post_details(client: TestClient, bill_id: int, subscriber_id: int):
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
