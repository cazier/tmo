# mypy: disable-error-code="has-type,no-untyped-def"

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


def test_post_charges(client: TestClient, bill_id: int):
    charge = {"name": "taxes", "split": True, "total": 1.0}

    response = client.post("/api/charge", params={"bill": bill_id}, json=charge)
    assert response.status_code == 200 and response.json() == {**charge, "bill_id": bill_id}
