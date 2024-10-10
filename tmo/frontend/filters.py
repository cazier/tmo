import collections
import typing

from pydantic import validate_call

from tmo.db.models import Render
from tmo.db.schemas import BillRender


@validate_call
def generate_table(
    data: list[BillRender], dependents: dict[str, list[str]]
) -> tuple[dict[str, dict[str, list[typing.Any]]], dict[str, float], float]:
    present, previous = data

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
