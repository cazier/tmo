# mypy: disable-error-code="no-untyped-def,call-arg,arg-type"
import contextlib
import dataclasses
import datetime
import decimal
import itertools
import random
import types
import typing

import faker
import pytest

from tests.helpers import phone_number
from tmo.config import config
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
    charges: list[typing.Any] = dataclasses.field(default_factory=list)
    subscribers: list[typing.Any] = dataclasses.field(default_factory=list)


def test_split():
    assert "first" == filters._split("first")
    assert "first" == filters._split("first second")
    assert "first" == filters._split("first second third")

    assert "" == filters._split("")


@pytest.mark.parametrize(("klass", "value"), (("is-currency-negative", -1), ("is-currency-zero", 0), ("", 1)))
def test_currency_class(klass: str, value: typing.Any):
    assert klass == filters.currency_class(value)


def bill(
    month: typing.Any = None,
    total: typing.Any = None,
    current: typing.Any = None,
    previous: typing.Any = None,
) -> filters.BillsRender:
    keys = ("phone", "line", "insurance", "usage", "data")

    if total and not current:
        current = 1

    if isinstance(current, int):
        current = [
            NS(
                id=i,
                name=str(i),
                number=str(i),
                details=NS(
                    **{key: decimal.Decimal((num := int(f"{1 + i}" * 2))) for key in keys},
                    minutes=num,
                    messages=num,
                    total=num,
                ),
            )
            for i in range(current)
        ]

    if isinstance(previous, int):
        previous = [
            NS(
                id=i,
                name=str(i),
                number=str(i),
                details=NS(
                    **{key: decimal.Decimal((num := int(f"{1 + i}" * 3))) for key in keys},
                    minutes=num,
                    messages=num,
                    total=num,
                ),
            )
            for i in range(previous)
        ]

    if current:
        current = NS(id=0, date=faker.Faker().date_object(), total=total or 0, subscribers=current)

    if previous:
        previous = NS(id=0, date=faker.Faker().date_object(), total=11, subscribers=previous)

    return filters.BillsRender.model_validate(
        dict(
            month=month or faker.Faker().date_object(),
            current=current or _TestObject(),
            previous=previous or _TestObject(),
        )
    )


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
        b = bill(month=datetime.date.fromisoformat(current))
        assert b.months == (datetime.date.fromisoformat(last), datetime.date.fromisoformat(next))

    def test_month_validator(self, faker: faker.Faker):
        month = faker.date_object()
        b = bill(month=month.replace(day=random.randint(2, 28)))
        assert b.month == month.replace(day=1)

    @pytest.mark.parametrize("input_field", filters.BillsRender.model_fields)
    def test_id_assignment(self, input_field: str):
        for field, info in bill().model_fields.items():
            for metadata in info.metadata:
                if field == input_field and isinstance(metadata, filters.Element):
                    assert metadata.id != ""

    def test_names(self, faker: faker.Faker):
        names = [faker.name() for _ in range(random.randint(10, 30))]
        b = filters.BillsRender.model_construct(current=NS(subscribers=[NS(name=name) for name in names]))
        assert list(b.names) == [*names]

    def test_total(self, faker: faker.Faker):
        b = bill(total=100)
        assert b.total == decimal.Decimal(100)

    @pytest.mark.parametrize(("diff"), (1, 0, -1), ids=("more", "equal", "fewer"))
    def test_recap(self, diff: int):
        b = bill(current=3, previous=3 + diff)
        check = [decimal.Decimal(111), decimal.Decimal(222), decimal.Decimal(333)]

        if diff == -1:
            check = [decimal.Decimal(111), decimal.Decimal(222), decimal.Decimal(0)]

        assert list(b.recap) == check

    @pytest.mark.parametrize("key", ("name", "number"))
    @pytest.mark.parametrize("success", (True, False), ids=("success", "failure"))
    def test_lookup(self, key: str, success: bool, faker: faker.Faker):
        subscribers = [NS(name=faker.name(), number=phone_number()) for _ in range(20)]

        b = filters.BillsRender.model_construct(current=NS(subscribers=subscribers))

        if success:
            lookup = random.choice(subscribers)
            found = b._lookup_subscriber(**{key: getattr(lookup, key)})
            assert found.name == lookup.name and found.number == lookup.number

        else:
            with pytest.raises(LookupError, match="Could not find the user: InvalidNameOrNumber"):
                b._lookup_subscriber(**{key: "InvalidNameOrNumber"})

    def test_lookup_invalid_usage(self, faker: faker.Faker):
        subscribers = [NS(name=faker.name(), number=phone_number()) for _ in range(20)]

        b = filters.BillsRender.model_construct(current=NS(subscribers=subscribers))

        with pytest.raises(ValueError, match="Must supply exactly one of name or number, but not both"):
            b._lookup_subscriber(name="InvalidNameOrNumber", number="InvalidNameOrNumber")

    def test_owed(self, faker: faker.Faker):
        names = [
            NS(name=faker.name(), number=phone_number(), details=NS(total=decimal.Decimal(random.randint(0, 100))))
            for _ in range(20)
        ]

        steps = [0, *sorted(random.sample(range(20), 5)), len(names)]
        dependents = {}
        total = {}

        for first, last in itertools.pairwise(steps):
            dependents[names[first].number] = [subscriber.number for subscriber in names[first:last]]
            total[names[first].name] = sum(subscriber.details.total for subscriber in names[first:last])

        b = filters.BillsRender.model_construct(current=NS(subscribers=names))

        with config.patch(frontend={"dependents": dependents}):
            assert b.owed == total

    def test_charges(self):
        current = [
            NS(name="111", total=decimal.Decimal(111)),
            NS(name="222", total=decimal.Decimal(222)),
        ]

        previous = [
            NS(name="111", total=decimal.Decimal(1)),
            NS(name="333", total=decimal.Decimal(3)),
        ]

        check = [
            {"name": "111", "present": decimal.Decimal(111), "previous": decimal.Decimal(1)},
            {"name": "222", "present": decimal.Decimal(222), "previous": decimal.Decimal(0)},
        ]

        b = filters.BillsRender.model_construct(current=NS(charges=current), previous=NS(charges=previous))
        assert [c.model_dump() for c in b.charges] == check

    @pytest.mark.parametrize(
        ("field", "cm"),
        (
            ("phone", contextlib.nullcontext()),
            ("month", pytest.raises(ValueError, match=r"Invalid \(non-transposed\) field 'month'")),
            ("invalid", pytest.raises(AttributeError, match=r"'.*' object has no attribute 'invalid'")),
        ),
        ids=("transposed", "non-transposed", "invalid"),
    )
    def test_get(self, field: str, cm, faker: faker.Faker):
        b = bill(current=3)

        with cm:
            values = b.get(field)
            assert [decimal.Decimal(11), decimal.Decimal(22), decimal.Decimal(33)] == [*values]

    @pytest.mark.parametrize(
        ("field", "cm"),
        (
            ("minutes", contextlib.nullcontext()),
            ("current", pytest.raises(TypeError, match="Field 'current' is not an Element type")),
            ("invalid", pytest.raises(KeyError, match="'invalid'")),
        ),
        ids=("valid", "no-element", "invalid"),
    )
    def test_get_element(self, field: str, cm):
        with cm:
            element = filters.BillsRender.get_element(field)
            assert isinstance(element, filters.Element) and element.id == field

    def test_fields_in_section_success(self):
        assert ["phone", "line", "insurance", "usage"] == [
            field for field, _ in filters.BillsRender.fields_in_section("charges")
        ]
        assert ["minutes", "messages", "data"] == [field for field, _ in filters.BillsRender.fields_in_section("usage")]

    def test_fields_in_section_failure(self, faker: faker.Faker):
        assert [] == [*filters.BillsRender.fields_in_section(faker.first_name())]

    def test_transpose(self, faker: faker.Faker):
        current = NS(
            date=faker.date_object(),
            total=decimal.Decimal(random.randint(0, 100)),
            id=random.randint(1, 100),
            charges=[],
            subscribers=[
                NS(
                    number=phone_number(),
                    name=faker.name(),
                    id=1,
                    details=NS(
                        phone=decimal.Decimal(10),
                        line=decimal.Decimal(11),
                        insurance=decimal.Decimal(12),
                        usage=decimal.Decimal(13),
                        total=decimal.Decimal(14),
                        minutes=15,
                        messages=16,
                        data=decimal.Decimal(16),
                    ),
                ),
                NS(
                    number=phone_number(),
                    name=faker.name(),
                    id=1,
                    details=NS(
                        phone=decimal.Decimal(20),
                        line=decimal.Decimal(21),
                        insurance=decimal.Decimal(22),
                        usage=decimal.Decimal(23),
                        total=decimal.Decimal(24),
                        minutes=25,
                        messages=26,
                        data=decimal.Decimal(26),
                    ),
                ),
                NS(
                    number=phone_number(),
                    name=faker.name(),
                    id=1,
                    details=NS(
                        phone=decimal.Decimal(30),
                        line=decimal.Decimal(31),
                        insurance=decimal.Decimal(32),
                        usage=decimal.Decimal(33),
                        total=decimal.Decimal(34),
                        minutes=35,
                        messages=36,
                        data=decimal.Decimal(36),
                    ),
                ),
            ],
        )

        b = filters.BillsRender(
            month=faker.date_object(),
            current=current,
            previous=NS(
                date=faker.date_object(),
                total=decimal.Decimal(100),
                id=1,
                charges=[],
                subscribers=[],
            ),
        )

        for field in ("phone", "line", "insurance", "usage", "minutes", "messages", "data"):
            for first, second in itertools.pairwise(getattr(b, field)):
                assert first == second - 10
