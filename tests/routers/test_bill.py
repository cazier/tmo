# mypy: disable-error-code="has-type,no-untyped-def"
import typing
import datetime
import random

import pytest
from fastapi.testclient import TestClient

from tmo.db.models.tables import Bill

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.fixture
def details(bill: Bill, database_values: dict[str, list[dict[str, typing.Any]]]):
    resp = {
        "charges": [
            {key: value for key, value in charge.items() if not key.endswith("id")}
            for charge in database_values["charge"]
            if charge["bill_id"] == bill.id
        ],
        "subscribers": [
            {key: value for key, value in subscriber.items()}
            for subscriber in database_values["subscriber"]
            if subscriber["id"]
            in {link["subscriber_id"] for link in database_values["billsubscriberlink"] if link["bill_id"] == bill.id}
        ],
    }

    for detail in database_values["detail"]:
        if detail["bill_id"] == bill.id:
            for subscriber in resp["subscribers"]:
                if subscriber.get("id", None) == detail["subscriber_id"]:
                    subscriber["total"] = detail["total"]

    return resp

@pytest.fixture
def previous_ids(database_values: dict[str, list[dict[str, typing.Any]]], request: pytest.FixtureRequest) -> tuple[datetime.date, list[int]]:
    match request.param:
        case "latest":
            return datetime.date.today(), [bill['id'] for bill in database_values['bill'][:-3:-1]]

        case "random":
            date = random.choice(database_values['bill'][1:])
            return datetime.date.fromisoformat(date['date']), [date['id'], date['id'] - 1]

@pytest.mark.parametrize(("previous_ids"), ["latest", "random"], indirect=True)
def test_get_previous_ids(previous_ids: tuple[datetime.date, list[int]], client: TestClient, ):
    date, ids = previous_ids
    
    response = client.get("/api/bill/previous-ids", params={'before': date.isoformat()} if date != datetime.date.today() else {})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == ids

def test_get_bills(client: TestClient, database_values: dict[str, list[dict[str, typing.Any]]]):
    response = client.get("/api/bill")
    assert response.status_code == 200
    assert len(response.json()) == len(database_values["bill"])
    assert response.json() == sorted(response.json(), key=lambda k: k["id"])


def test_get_bill(client: TestClient, bill: Bill, details: list[dict[str, int | float]]):
    response = client.get(f"/api/bill/{bill.id}")
    assert response.status_code == 200

    json = bill.model_dump(mode="json")
    data = response.json()

    assert json == {"date": data.pop("date"), "id": data.pop("id"), "total": data.pop("total")}
    assert details == data
