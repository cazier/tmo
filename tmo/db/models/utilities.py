from __future__ import annotations

import dataclasses
import decimal
import itertools
import typing

from pydantic import PlainSerializer
from sqlmodel import Field, SQLModel

_T = typing.TypeVar("_T")
JsonDecimal = typing.Annotated[decimal.Decimal, PlainSerializer(float, return_type=float, when_used="json")]


## Utility classes
def decimal_field(
    default: decimal.Decimal | int | float = 0,
    max_digits: int = 8,
    decimal_places: int = 2,
    **kwargs: dict[str, typing.Any],
) -> Field:
    return Field(default=default, max_digits=max_digits, decimal_places=decimal_places, **kwargs)


@dataclasses.dataclass(order=True)
class Render:
    @staticmethod
    def noop(value: _T) -> _T:
        return value

    section: str
    order: int
    name: str = dataclasses.field(default="", compare=False)
    formatter: typing.Callable[[_T], _T] = dataclasses.field(default=noop, compare=False)

    def with_name(self, fallback: str) -> Render:
        if self.name == "":
            self.name = fallback

        return self


class AnnotatedSQLModel(SQLModel):
    @typing.overload
    def fields_by_annotation(self, string: str) -> typing.Iterable[tuple[str, str]]:
        ...

    @typing.overload
    def fields_by_annotation(self, klass: type[_T]) -> typing.Iterable[tuple[str, _T]]:
        ...

    def fields_by_annotation(self, string="", klass=None):
        for name, field in itertools.chain(self.model_fields.items(), self.model_computed_fields.items()):
            for item in getattr(field, "metadata", getattr(getattr(field, "return_type", None), "__metadata__", [])):
                if klass and isinstance(item, klass):
                    yield name, item
                elif isinstance(item, str) and item == string:
                    yield name, item
