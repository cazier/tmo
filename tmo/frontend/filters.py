import collections
import functools
import itertools
import typing

from pydantic import fields, validate_call
from sqlmodel import SQLModel

from tmo.db.models import Render
from tmo.db.schemas import BillRender

_T = typing.TypeVar("_T")
_M = typing.TypeVar("_M", bound=SQLModel)


@validate_call
def table(data: list[BillRender]) -> dict[str, dict[str, list[typing.Any]]]:
    present, previous = data

    resp = {section: collections.defaultdict(list) for section in BillRender.sections}

    for subscriber in present.subscribers:
        for key, schema in subscriber.fields_by_annotation(klass=Render):
            resp[schema.section][schema.name].append(schema.formatter(getattr(subscriber, key)))

        for key, schema in subscriber.details.fields_by_annotation(klass=Render):
            resp[schema.section][schema.name].append(schema.formatter(getattr(subscriber.details, key)))

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


def currency_class(value: int | float) -> str:
    if value < 0:
        return " is-currency-negative"

    if value == 0:
        return " is-currency-zero"

    return ""


@functools.lru_cache(typed=True)
def keys(model: _M, *models: _M) -> dict[str, Render]:
    def _schema(name: str, field: fields.FieldInfo | fields.ComputedFieldInfo) -> tuple[str, Render | None]:
        if isinstance(field, fields.FieldInfo):
            items = field.metadata

        if isinstance(field, fields.ComputedFieldInfo):
            items = field.return_type.__metadata__

        for item in items:
            if isinstance(item, Render):
                return name, item

        return name, None

    return {
        key: field.with_name(key)
        for model in map(lambda m: m.model_construct(), (model, *models))
        for key, field in sorted(
            (
                (name, schema)
                for name, schema in itertools.starmap(
                    _schema,
                    itertools.chain(
                        model.model_fields.items(),
                        model.model_computed_fields.items(),
                    ),
                )
                if schema is not None
            ),
        )
    }
