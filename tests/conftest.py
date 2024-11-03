# mypy: disable-error-code="no-untyped-def"

import calendar
import datetime
import pathlib
import random
import typing

import faker
import fastapi.testclient
import pydantic
import pytest
from sqlmodel import Session, SQLModel

from tests.helpers import phone_number
from tmo import config
from tmo.db.models import Bill, Subscriber

USERS: int = 10
YEARS: int = 5
SERVICES: tuple[str, ...] = ("netflix", "hulu")
FIELDS: tuple[str, ...] = ("phone", "line", "insurance", "usage", "minutes", "messages", "data")


@pytest.fixture(autouse=True, scope="session")
def _setup_database(subscribers: list[dict[str, str]], bills: set[datetime.date], database: dict[str, typing.Any]):
    def _numbers() -> dict[str, int | float]:
        def _number(kind: str) -> int | float:
            match kind:
                case "phone" | "line" | "insurance" | "usage" | "data":
                    return float(f"{random.randint(0, 30)}.{random.randint(0, 99)}")

                case _:  # "minutes" | "messages":
                    return random.randint(0, 10000)

        return {key: _number(key) for key in FIELDS}

    for month in bills:
        database[month.strftime("%Y.%m.%d")] = {
            "subscribers": [{**subscriber, **_numbers()} for subscriber in subscribers],
            "other": {random.choices(SERVICES, [90, 10], k=1)[0]: random.randint(5, 10)},
        }

    yield


@pytest.fixture(scope="session")
def bills():
    def _get_date(year: int, month: int) -> datetime.date:
        return datetime.date(year, month, random.randint(1, calendar.monthrange(year, month)[1]))

    start = random.randint(2000, 2010)
    return {_get_date(start + year, month) for month in range(1, 13) for year in range(YEARS)}


@pytest.fixture(scope="session")
def subscribers():
    _faker = faker.Faker()
    return [{"number": phone_number(), "name": _faker.name(), "id": index + 1} for index in range(USERS)]


@pytest.fixture(scope="session")
def database():
    _db: dict[str, typing.Any] = {}
    yield _db


@pytest.fixture(scope="session")
def session():
    with config.patch(database={"dialect": "memory", "echo": True}):
        from tmo.db.engines import engine

        with Session(engine) as _session:
            yield _session

        SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def client(session: Session, tmp_path_factory: pytest.TempPathFactory):
    def _get_session_test():
        return session

    path = tmp_path_factory.getbasetemp().joinpath("config.toml")

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("TMO_UVICORN_CONFIG_PATH", str(path))
        path.write_text("", encoding="utf8")

        from tmo.dependencies import get_session
        from tmo.web import app

        with fastapi.testclient.TestClient(app) as client:
            app.dependency_overrides[get_session] = _get_session_test
            yield client


# def fields(model: pydantic.BaseModel) -> dict[str, pydantic.fields.FieldInfo]:
#     return model.model_fields
