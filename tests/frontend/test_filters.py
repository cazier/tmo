# mypy: disable-error-code="no-untyped-def"

import datetime
import random
import typing

import faker
import pytest

from tmo.db.schemas import SubscriberReadWithDetails
from tmo.frontend import filters


def test_split():
    assert "first" == filters._split("first")
    assert "first" == filters._split("first second")
    assert "first" == filters._split("first second third")

    assert "" == filters._split("")


@pytest.mark.parametrize(("klass", "value"), (("is-currency-negative", -1), ("is-currency-zero", 0), ("", 1)))
def test_currency_class(klass: str, value: typing.Any):
    assert klass == filters.currency_class(value)


class TestBillsRender:
    def test_names(self, faker: faker.Faker):
        names = [faker.name() for _ in range(random.randint(10, 30))]
        b = filters.BillsRender.model_construct(
            subscribers=[SubscriberReadWithDetails.model_construct(name=name) for name in names]
        )
        assert list(b.names) == ["", *names]

    @pytest.mark.parametrize(
        ("current", "last", "next"),
        (
            ("2024-01-01", "2023-12-01", "2024-02-01"),
            ("2024-06-01", "2024-05-01", "2024-07-01"),
            ("2024-12-01", "2024-11-01", "2025-01-01"),
        ),
        ids=("january", "june", "december"),
    )
    def test_month_calculation(self, current: str, last: str, next: str):
        b = filters.BillsRender.model_construct(month=datetime.date.fromisoformat(current))
        assert b.months == (datetime.date.fromisoformat(last), datetime.date.fromisoformat(next))
