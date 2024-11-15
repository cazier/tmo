# mypy: disable-error-code="no-untyped-def"
import collections
import json
import pathlib
import re

import fastapi.testclient
import pytest
from sqlmodel import Session, SQLModel, text

from tmo import config

USERS: int = 10
YEARS: int = 5
SERVICES: tuple[str, ...] = ("netflix", "hulu")
FIELDS: tuple[str, ...] = ("phone", "line", "insurance", "usage", "minutes", "messages", "data")


@pytest.fixture(scope="session")
def session():
    with config.patch(database={"dialect": "memory", "echo": True}):
        from tmo.db.engines import start_engine

        engine = start_engine(connect_args={"check_same_thread": False})

        with Session(engine, autoflush=False) as _session:
            yield _session

        SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def database(session: Session):
    raw_data = pathlib.Path(__file__).parent.joinpath("data.sql").read_text("ascii")

    data = collections.defaultdict(list)
    pattern = re.compile(r"INSERT INTO (\w+) VALUES\((.*)\);")

    for line in raw_data.splitlines():
        session.exec(text(line))

        if match := pattern.match(line):
            table, _fields = match.groups()
            data[table].append([json.loads(field.strip()) for field in _fields.strip().split(",")])

    yield data


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
