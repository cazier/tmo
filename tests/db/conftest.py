# pylint: disable=redefined-outer-name
# mypy: disable-error-code="no-untyped-def"

import calendar
import datetime
import random
import typing

import faker
import pydantic
import pytest
from sqlmodel import Session, SQLModel

from tmo import config

USERS: int = 10
YEARS: int = 5
SERVICES: tuple[str, ...] = ("netflix", "hulu")
FIELDS: tuple[str, ...] = ("phone", "line", "insurance", "usage", "minutes", "messages", "data")


@pytest.fixture(autouse=True, scope="session")
def _setup_database(subscribers: list[dict[str, str]], database: dict[str, typing.Any]):
    def _months() -> set[datetime.date]:
        def _get_date(year: int, month: int) -> datetime.date:
            return datetime.date(year, month, random.randint(1, calendar.monthrange(year, month)[1]))

        start = random.randint(2000, 2010)
        return {_get_date(start + year, month) for month in range(1, 13) for year in range(YEARS)}

    def _numbers() -> dict[str, int | float]:
        def _number(kind: str) -> int | float:
            match kind:
                case "phone" | "line" | "insurance" | "usage" | "data":
                    return float(f"{random.randint(0, 30)}.{random.randint(0, 99)}")

                case _:  # "minutes" | "messages":
                    return random.randint(0, 10000)

        return {key: _number(key) for key in FIELDS}

    for month in _months():
        database[month.strftime("%Y.%m.%d")] = {
            "subscribers": [{**subscriber, **_numbers()} for subscriber in subscribers],
            "other": {random.choices(SERVICES, [90, 10], k=1)[0]: random.randint(5, 10)},
        }

    yield


@pytest.fixture(scope="session")
def subscribers():
    def _phone_number() -> str:
        return f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}-{random.randint(0, 9999):04d}"

    _faker = faker.Faker()
    return [{"number": _phone_number(), "name": _faker.name(), "id": index + 1} for index in range(USERS)]


@pytest.fixture(scope="session")
def database():
    _db: dict[str, typing.Any] = {}
    yield _db


@pytest.fixture
def session():
    with config.patch(database={"dialect": "memory"}):
        from tmo.db.engines import start_engine  # pylint: disable=import-outside-toplevel

        engine = start_engine()
        SQLModel.metadata.create_all(engine)

        with Session(engine) as _session:
            yield _session

        SQLModel.metadata.drop_all(engine)


def fields(model: pydantic.BaseModel) -> dict[str, pydantic.fields.FieldInfo]:
    return model.model_fields
