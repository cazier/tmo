import collections
import dataclasses
import datetime
import decimal
import typing

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator, validate_call

from ..config import config
from ..db.models import Bill, Charge, Render
from ..db.schemas import BillRender, SubscriberReadWithDetails
from ..lib.utilities import get_attr_item


@dataclasses.dataclass
class Element:
    id: str
    title: str
    is_currency: bool = False


class Transpose:
    pass


_list = (Field(default_factory=list), (_transpose_ := Transpose()))


class BillsRender(BaseModel):
    month: datetime.date
    total: decimal.Decimal

    current: typing.Annotated[BillRender, Field(exclude=True)]
    previous: typing.Annotated[BillRender, Field(exclude=True)]

    phone: typing.Annotated[list[decimal.Decimal], *_list, Element("phone", "Phone Cost", is_currency=True)]
    line: typing.Annotated[list[decimal.Decimal], *_list, Element("line", "Line Cost", is_currency=True)]
    insurance: typing.Annotated[list[decimal.Decimal], *_list, Element("insurance", "Insurance", is_currency=True)]
    usage: typing.Annotated[list[decimal.Decimal], *_list, Element("usage", "Usage Charges", is_currency=True)]

    minutes: typing.Annotated[list[int], *_list, Element("minutes", "Minutes (min)")]
    messages: typing.Annotated[list[int], *_list, Element("messages", "Messages (#)")]
    data: typing.Annotated[list[decimal.Decimal], *_list, Element("data", "Data (GB)")]

    @field_validator("month", mode="after")
    @classmethod
    def _month(cls, v: datetime.date) -> datetime.date:
        return v.replace(day=1)

    @property
    def months(self) -> typing.Annotated[tuple[datetime.date, datetime.date], Element("date", "Date")]:
        return (
            (self.month - datetime.timedelta(days=1)).replace(day=1),
            (self.month + datetime.timedelta(days=45)).replace(day=1),
        )

    @property
    def names(self) -> typing.Iterator[str]:
        yield ""
        yield from (subscriber.name for subscriber in self.current.subscribers)

    @property
    def recap(self) -> typing.Iterator[decimal.Decimal]:
        previous = {subscriber.number: subscriber.details.total for subscriber in self.previous.subscribers}

        yield from (previous.get(current.number, decimal.Decimal(0)) for current in self.current.subscribers)

    @property
    def owed(self) -> dict[str, decimal.Decimal]:
        owed: dict[str, decimal.Decimal] = collections.defaultdict(decimal.Decimal)

        for subscriber in self.current.subscribers:
            if subscriber.number not in config.frontend.dependents:
                continue

            for dependent in config.frontend.dependents[subscriber.number]:
                owed[subscriber.name] += self._lookup_subscriber(number=dependent).details.total

        return owed

    def _lookup_subscriber(self, *, name: str = "", number: str = "") -> SubscriberReadWithDetails:
        number = number.replace("-", "")

        if name and number or (name == "" and number == ""):
            raise ValueError("Must supply exactly one of name or number, but not both.")

        for subscriber in self.current.subscribers:
            if number and subscriber.number.replace("-", "") == number:
                return subscriber
            if name and subscriber.name == name:
                return subscriber

        raise LookupError(f"Could not find the user: {name if name else number}")

    @model_validator(mode="before")
    @classmethod
    def _transpose_subscriber_info(cls, data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        _data = collections.defaultdict(list, **data)

        for field, info in cls.model_fields.items():
            if _transpose_ not in info.metadata:
                continue

            for subscriber in get_attr_item(data, "current", "subscribers", default=[]):
                _data[field].append(get_attr_item(subscriber, "details", field))

        return _data


@validate_call
def generate_table(
    data: list[BillRender], dependents: dict[str, list[str]]
) -> tuple[dict[str, dict[str, list[typing.Any]]], dict[str, float], float]:
    present, previous = data

    M = BillsRender(month=present.date, total=1.23, current=present, previous=previous)

    breakpoint()

    total = present.total

    resp = {section: collections.defaultdict(list) for section in BillRender.sections}
    resp.update(shared=[], owed={name: 0.0 for name in dependents})
    _lookup = {name: target for target, names in dependents.items() for name in names}

    split = sum([charge.total for charge in present.charges if charge.split]) / len(present.subscribers)

    for subscriber in present.subscribers:
        for key, schema in subscriber.fields_by_annotation(klass=Render):
            resp[schema.section][(key, schema.name)].append(schema.formatter(getattr(subscriber, key)))

        for key, schema in subscriber.details.fields_by_annotation(klass=Render):
            resp[schema.section][(key, schema.name)].append(schema.formatter(getattr(subscriber.details, key)))

            if key == "total":
                for past_subscriber in previous.subscribers:
                    if subscriber.id == past_subscriber.id:
                        resp["recap"]["(Last Month)"].append(schema.formatter(getattr(past_subscriber.details, key)))
                        break
                else:
                    resp["recap"]["(Last Month)"].append(schema.formatter(0))

        if target := _lookup.get(_split(subscriber.name)):
            resp["owed"][target] += float(subscriber.details.total) + float(split)

    for charge in present.charges:
        values = {"name": charge.name, "present": charge.total, "previous": 0}

        for past_charge in previous.charges:
            if past_charge.name == charge.name:
                values["previous"] = past_charge.total
                break

        resp["shared"].append(values)

    resp["owed"] = {key: value for key, value in resp["owed"].items() if value != 0}

    from rich import print

    print(present)

    print(resp)

    return total, resp


@validate_call
def generate_charts(data: BillRender, colors: dict[str, str]) -> dict[str, dict[str, str | int | float]]:
    resp = collections.defaultdict(dict)

    for subscriber in data.subscribers:
        for key, _ in subscriber.details.fields_by_annotation(string="#"):
            resp[key][subscriber.name] = float(getattr(subscriber.details, key))

        resp["colors"][subscriber.name] = colors[_split(subscriber.name)]

    return resp


def _split(string: str) -> str:
    return string.split(" ")[0]


def currency_class(value: int | float) -> str:
    if value < 0:
        return "is-currency-negative"

    if value == 0:
        return "is-currency-zero"

    return ""
