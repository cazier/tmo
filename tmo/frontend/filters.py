import typing

from tmo.db.models import MonthValidator, keys

_T = typing.TypeVar("_T")


def table(data: list[dict[str, _T]]) -> dict[str, dict[str, list[str]]]:
    return {
        section: {
            schema["name"]: [schema["formatter"](subscriber[key]) for subscriber in data]
            for key, schema in keys(MonthValidator.MVSubscriber).items()
            if schema["section"] == section
        }
        for section in MonthValidator.sections
    }


def previous(data: list[dict[str, _T]]) -> dict[str, list[str]]:
    return table(data).get("summary", {})


def currency_class(value: int | float) -> str:
    if value < 0:
        return " is-currency-negative"

    if value == 0:
        return " is-currency-zero"

    return ""
