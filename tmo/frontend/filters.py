import functools
import itertools
import typing

from pydantic import fields
from sqlmodel import SQLModel

from tmo.db.models import Render
from tmo.db.schemas import BillRender

_T = typing.TypeVar("_T")
_M = typing.TypeVar("_M", bound=SQLModel)


def table(data: list[dict[str, _T]]) -> dict[str, dict[str, list[_T]]]:
    return {
        section: {
            schema.name: [schema.formatter(subscriber[key]) for subscriber in data]
            for key, schema in keys(BillRender).items()
            if schema.section == section
        }
        for section in BillRender.sections
    }


def previous(data: list[dict[str, _T]]) -> dict[str, list[_T]]:
    return table(data).get("summary", {})


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
