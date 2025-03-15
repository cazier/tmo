# mypy: disable-error-code="has-type,no-untyped-def"

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.mark.parametrize("bill_id", (True, False), ids=("bill", "no_bill"), indirect=True)
@pytest.mark.parametrize("subscriber_id", (True, False), ids=("subscriber", "no_subscriber"), indirect=True)
def test_post_details(client: TestClient, bill_id: tuple[int, bool], subscriber_id: tuple[int, bool]):
    _bill_id, _bill_exists = bill_id
    _subscriber_id, _subscriber_exists = subscriber_id

    detail = {
        "phone": 1.0,
        "line": 2.0,
        "insurance": 3.0,
        "usage": 4.0,
        "minutes": 5,
        "messages": 6,
        "data": 7.0,
    }

    response = client.post("/api/detail", params={"bill": _bill_id, "subscriber": _subscriber_id}, json=detail)

    if _bill_exists and _subscriber_exists:
        assert response.status_code == 200 and (id := response.json()["id"])
        assert response.json() == {
            **detail,
            "total": 10.0,
            "bill_id": _bill_id,
            "subscriber_id": _subscriber_id,
            "id": id,
        }

        response = client.get(f"/api/bill/{_bill_id}")
        assert response.status_code == 200 and _subscriber_id in [
            subscriber["id"] for subscriber in response.json()["subscribers"]
        ]

        response = client.get(f"/api/subscriber/{_subscriber_id}")
        assert response.status_code == 200 and id in [detail["id"] for detail in response.json()["details"]]

    elif _bill_exists and not _subscriber_exists:
        assert response.status_code == 404 and response.json() == {"detail": "Subscriber could not be found"}

    else:
        assert response.status_code == 404 and response.json() == {"detail": "Bill could not be found"}
