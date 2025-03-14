# mypy: disable-error-code="has-type,no-untyped-def"

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.mark.parametrize("bill_id", (True, False), ids=("bill", "no_bill"), indirect=True)
def test_post_charges(client: TestClient, bill_id: tuple[int, bool]):
    id, valid = bill_id
    charge = {"name": "taxes", "split": True, "total": 1.0}

    response = client.post("/api/charge", params={"bill": id}, json=charge)

    if valid:
        assert response.status_code == 200 and response.json() == {**charge, "bill_id": id}

    else:
        assert response.status_code == 404 and response.json() == {"detail": "Bill could not be found"}
