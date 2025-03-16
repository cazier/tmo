# mypy: disable-error-code="has-type,no-untyped-def"
import copy
import datetime
import random
import typing

import arrow
import pytest
from fastapi.testclient import TestClient

from tmo.db.models.tables import Bill

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.fixture
def details(bill: Bill, database_values: dict[str, list[dict[str, typing.Any]]]):
    database_values = copy.deepcopy(database_values)
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
                    subscriber["details"] = detail

    return resp


@pytest.fixture
def previous_ids(
    database_values: dict[str, list[dict[str, typing.Any]]], request: pytest.FixtureRequest
) -> tuple[datetime.date, list[int]]:
    if request.param == "latest":
        return datetime.date.today(), [bill["id"] for bill in database_values["bill"][:-3:-1]]

    date = random.choice(database_values["bill"][1:])
    return datetime.date.fromisoformat(date["date"]), [date["id"], date["id"] - 1]


@pytest.mark.parametrize(("previous_ids"), ["latest", "random"], indirect=True)
def test_get_previous_ids(
    previous_ids: tuple[datetime.date, list[int]],
    client: TestClient,
):
    date, ids = previous_ids

    response = client.get(
        "/api/bill/previous-ids", params={"before": date.isoformat()} if date != datetime.date.today() else {}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == ids


def test_get_bills(client: TestClient, database_values: dict[str, list[dict[str, typing.Any]]]):
    response = client.get("/api/bill")
    assert response.status_code == 200
    assert len(response.json()) == len(database_values["bill"])
    assert response.json() == sorted(response.json(), key=lambda k: k["id"])


@pytest.mark.parametrize("exists", (True, False))
@pytest.mark.parametrize("by", ("date", "id"))
def test_get_bill(by: typing.Literal["date", "id"], exists: bool, client: TestClient, bill: Bill, details: typing.Any):
    if exists:
        if by == "date":
            endpoint = f"/api/bill/{bill.date.year}/{bill.date.month}"
        else:
            endpoint = f"/api/bill/{bill.id}"

        response = client.get(endpoint)
        assert response.status_code == 200

        json = bill.model_dump(mode="json")
        data = response.json()

        assert json == {"date": data.pop("date"), "id": data.pop("id"), "total": data.pop("total")}

        details = {
            "charges": details["charges"],
            "subscribers": [
                {
                    key: value
                    for key, value in {**subscriber, "total": subscriber["details"]["total"]}.items()
                    if key in ("id", "name", "number", "format", "total")
                }
                for subscriber in details["subscribers"]
            ],
        }

        assert details == data

    else:
        if by == "date":
            endpoint = f"/api/bill/{bill.date.year + 100}/{bill.date.month}"
        else:
            endpoint = f"/api/bill/{bill.id + 100}"

        response = client.get(endpoint)
        assert response.status_code == 404 and response.json() == {"detail": "Bill could not be found"}


@pytest.mark.parametrize("exists", (True, False))
def test_get_bill_detailed(exists: bool, client: TestClient, bill: Bill, details: typing.Any):
    if exists:
        response = client.get(f"/api/bill/{bill.id}/detailed")
        assert response.status_code == 200

        json = bill.model_dump(mode="json")
        data = response.json()

        assert json == {"date": data.pop("date"), "id": data.pop("id"), "total": data.pop("total")}

        details = {
            "charges": details["charges"],
            "subscribers": [
                {
                    key: value
                    if key != "details"
                    else {key: value_ for key, value_ in value.items() if key not in ("id", "bill_id", "subscriber_id")}
                    for key, value in subscriber.items()
                }
                for subscriber in details["subscribers"]
            ],
        }

        assert details == data

    else:
        response = client.get(f"/api/bill/{bill.id + 100}/detailed")
        assert response.status_code == 404 and response.json() == {"detail": "Bill could not be found"}


@pytest.mark.parametrize("state", (-1, 0, 1), ids=("exists", "invalid day", "success"))
def test_post_bill(state: int, client: TestClient, bill: Bill, database_values: dict[str, list[dict[str, typing.Any]]]):
    if state == -1:
        response = client.post("/api/bill", json={"date": bill.date.isoformat()})
        assert response.status_code == 409 and response.json() == {
            "detail": f"A bill with the date {bill.date} already exists (ID={bill.id})"
        }

    if state == 0:
        response = client.post("/api/bill", json={"date": "2021-05-08"})
        assert response.status_code == 400 and response.json() == {
            "detail": "Bill day must be the first day of the month"
        }

    if state == 1:
        date = arrow.get(database_values["bill"][-1]["date"]).shift(years=+1)
        total = float(f"{random.randint(100, 400)}.{random.randint(0, 99)}")

        response = client.post("/api/bill", json={"date": date.date().isoformat(), "total": total})

        assert response.status_code == 200 and (id := response.json()["id"])
        assert response.json() == {"date": date.date().isoformat(), "total": total, "id": id}
