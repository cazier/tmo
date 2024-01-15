import collections
import typing

from pydantic import validate_call
from sqlmodel import SQLModel

from tmo.db.models import Render
from tmo.db.schemas import BillRender

_T = typing.TypeVar("_T")
_M = typing.TypeVar("_M", bound=SQLModel)


@validate_call
def generate_table(data: list[BillRender]) -> dict[str, dict[str, list[typing.Any]]]:
    present, previous = data

    resp = {section: collections.defaultdict(list) for section in BillRender.sections}

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

    for charge in present.charges:
        resp["shared"][charge.name] = {"present": charge.total}

        for past_charge in previous.charges:
            if past_charge.name == charge.name:
                amount = past_charge.total
                break
        else:
            amount = 0

        resp["shared"][charge.name]["past"] = amount

    return resp


@validate_call
def generate_charts(data: BillRender) -> dict[str, float]:
    resp = collections.defaultdict(dict)

    for subscriber in data.subscribers:
        for key, _ in subscriber.details.fields_by_annotation(string="#"):
            resp[key][subscriber.name] = float(getattr(subscriber.details, key))

    return resp


def currency_class(value: int | float) -> str:
    if value < 0:
        return " is-currency-negative"

    if value == 0:
        return " is-currency-zero"

    return ""
