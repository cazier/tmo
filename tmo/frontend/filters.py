import collections
import decimal
import typing

import pydantic

from tmo.db.models import Charge, Render
from tmo.db.schemas import BillRender


class Row(pydantic.BaseModel):
    id: str
    title: str
    values: list[decimal.Decimal | int] = pydantic.Field(default_factory=[])


class Section(pydantic.BaseModel):
    rows: list[Row] = pydantic.Field(default_factory=list)


_Section = typing.Annotated[Section, pydantic.Field(default_factory=Section)]


class Table(pydantic.BaseModel):
    total: decimal.Decimal

    names: list[str]
    charges: _Section
    usage: _Section
    summary: _Section
    recap: _Section
    shared: list[Charge] = pydantic.Field(default_factory=list)
    owed: dict[str, decimal.Decimal] = pydantic.Field(default_factory=dict)


@pydantic.validate_call
def generate_table(
    present: BillRender, previous: BillRender, **dependents: list[str]
) -> tuple[dict[str, dict[str, list[typing.Any]]], dict[str, float], float]:
    resp = {
        "total": present.total,
        "names": [],
        **{section: collections.defaultdict(list) for section in BillRender.sections},
    }
    resp.update(shared=[], owed={name: 0.0 for name in dependents})
    _lookup = {name: target for target, names in dependents.items() for name in names}

    for subscriber in present.subscribers:
        resp["names"].append(subscriber.name)
        # for key, schema in subscriber.fields_by_annotation(klass=Render):
        #     resp[schema.section].append(schema.formatter(getattr(subscriber, key)))

        for key, schema in subscriber.details.fields_by_annotation(klass=Render):
            resp[schema.section][schema.id].append(schema.formatter(getattr(subscriber.details, key)))

            if key == "total":
                for past_subscriber in previous.subscribers:
                    if subscriber.id == past_subscriber.id:
                        resp["recap"]["(Last Month)"].append(schema.formatter(getattr(past_subscriber.details, key)))
                        break
                else:
                    resp["recap"]["(Last Month)"].append(schema.formatter(0))

        if target := _lookup.get(_split(subscriber.name)):
            resp["owed"][target] += float(subscriber.details.total)

    for charge in present.charges:
        values = {"name": charge.name, "present": charge.total, "previous": 0}

        for past_charge in previous.charges:
            if past_charge.name == charge.name:
                values["previous"] = past_charge.total
                break

        resp["shared"].append(values)

    resp["owed"] = {key: value for key, value in resp["owed"].items() if value != 0}

    breakpoint()
    table = Table.model_validate(resp)

    from rich import print

    print("=" * 80)
    print(resp)
    print("=" * 80)

    return total, resp


@pydantic.validate_call
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
