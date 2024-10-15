# mypy: disable-error-code="no-untyped-def"

import dataclasses
import datetime
import decimal
import random
import types
import typing

import faker
import pytest

from tmo.frontend import filters


class NS(types.SimpleNamespace):
    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return []


@dataclasses.dataclass
class _TestObject:
    id: int = 0
    date: datetime.date = dataclasses.field(default_factory=datetime.date.today)
    charges: list = dataclasses.field(default_factory=list)
    subscribers: list = dataclasses.field(default_factory=list)


def test_split():
    assert "first" == filters._split("first")
    assert "first" == filters._split("first second")
    assert "first" == filters._split("first second third")

    assert "" == filters._split("")


@pytest.mark.parametrize(("klass", "value"), (("is-currency-negative", -1), ("is-currency-zero", 0), ("", 1)))
def test_currency_class(klass: str, value: typing.Any):
    assert klass == filters.currency_class(value)


class TestBillsRender:
    @pytest.mark.parametrize(
        ("current", "last", "next"),
        (
            ("2024-01-01", "2023-12-01", "2024-02-01"),
            ("2024-06-01", "2024-05-01", "2024-07-01"),
            ("2024-12-01", "2024-11-01", "2025-01-01"),
        ),
        ids=("january", "june", "december"),
    )
    def test_months_calculation(self, current: str, last: str, next: str):
        b = filters.BillsRender.model_construct(month=datetime.date.fromisoformat(current))
        assert b.months == (datetime.date.fromisoformat(last), datetime.date.fromisoformat(next))

    def test_month_validator(self, faker: faker.Faker):
        month = faker.date_object()
        b = filters.BillsRender(
            month=month.replace(day=random.randint(2, 28)), total=0, current=_TestObject(), previous=_TestObject()
        )
        assert b.month == month.replace(day=1)

    def test_names(self, faker: faker.Faker):
        names = [faker.name() for _ in range(random.randint(10, 30))]
        b = filters.BillsRender.model_construct(current=NS(subscribers=[NS(name=name) for name in names]))
        assert list(b.names) == ["", *names]

    @pytest.mark.parametrize(("diff"), (1, 0, -1), ids=("more", "equal", "fewer"))
    def test_recap(self, diff: int, faker: faker.Faker):
        current = [
            NS(number="111", details=NS(total=decimal.Decimal(1))),
            NS(number="222", details=NS(total=decimal.Decimal(2))),
            NS(number="333", details=NS(total=decimal.Decimal(3))),
        ]

        previous = [
            NS(number="111", details=NS(total=decimal.Decimal(11))),
            NS(number="222", details=NS(total=decimal.Decimal(22))),
            NS(number="333", details=NS(total=decimal.Decimal(33))),
        ]

        check = [decimal.Decimal(11), decimal.Decimal(22), decimal.Decimal(33)]

        if diff == 1:
            previous.pop(1)
            check = [decimal.Decimal(11), decimal.Decimal(0), decimal.Decimal(33)]

        if diff == -1:
            previous.append(NS(number="444", details=NS(total=decimal.Decimal(44))))

        b = filters.BillsRender.model_construct(current=NS(subscribers=current), previous=NS(subscribers=previous))
        assert list(b.recap) == check
