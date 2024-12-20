# mypy: disable-error-code="no-untyped-def"
import typing

import pytest
import time_machine
from fastapi.testclient import TestClient

from tmo.db.models import Bill

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


@pytest.fixture
def bill(bill: Bill):
    with time_machine.travel(bill.date):
        yield bill


@pytest.mark.parametrize(
    ("url", "status_code"),
    [
        ("/missing", 404),
        ("/bill/2020/13", 422),
    ],
)
def test_errors(url: str, status_code: int, client: TestClient):
    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize("by", ("current", "date"))
def test_page(by: typing.Literal["current", "date"], bill: Bill, client: TestClient) -> None:
    if by == "current":
        response = client.get("/bill")
    else:
        response = client.get(f"/bill/{bill.date.year}/{bill.date.month}")

    assert response.status_code == 200

    assert f"Bill { bill.date.year }.{bill.date.month:02d}" in response.text
