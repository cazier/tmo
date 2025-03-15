# mypy: disable-error-code="has-type,no-untyped-def"

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.mark.parametrize("bill_id", (True, False), ids=("bill", "no_bill"), indirect=True)
def test_post_charges(client: TestClient, bill_id: tuple[int, bool]):
    _bill_id, valid = bill_id
    charge = {"name": "taxes", "split": True, "total": 1.0}

    response = client.post("/api/charge", params={"bill": _bill_id}, json=charge)

    if valid:
        assert response.status_code == 200 and (id := response.json()["id"])
        assert response.json() == {**charge, "bill_id": _bill_id, "id": id}

        response = client.get(f"/api/bill/{_bill_id}")
        assert response.status_code == 200 and charge in response.json()["charges"]

    else:
        assert response.status_code == 404 and response.json() == {"detail": "Bill could not be found"}
