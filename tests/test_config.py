# mypy: disable-error-code="no-untyped-def"

import contextlib
import json
import pathlib
import random
import tomllib
import typing

import pytest
from faker import Faker

from tmo.config import Config, Frontend, Load, Memory, Sqlite


@pytest.fixture(scope="session")
def gen_data() -> str:
    return f"""
[database]
dialect = "sqlite"
path = "db.sqlite3"
echo = {random.choice(("true", "false"))}
clear = {random.choice(("true", "false"))}
"""


@pytest.fixture
def dictionary(request: pytest.FixtureRequest, tmp_path: pathlib.Path, gen_data: str) -> dict[str, typing.Any]:
    path = tmp_path.joinpath(f"config.{request.param}")
    data = tomllib.loads(gen_data)

    match request.param:
        case "toml" | "string":
            path.write_text(gen_data, encoding="utf8")
        case "json":
            gen_data = json.dumps(data)
            path.write_text(gen_data, encoding="utf8")

    return data


@pytest.mark.parametrize(
    ("format", "dictionary", "expectation"),
    (
        ("toml", "toml", contextlib.nullcontext()),
        ("string", "toml", contextlib.nullcontext()),
        ("json", "json", contextlib.nullcontext()),
        ("yaml", "yaml", pytest.raises(TypeError)),
    ),
    indirect=["dictionary"],
    ids=("toml", "string", "json", "yaml"),
)
def test_from_file(format: str, dictionary: dict[str, typing.Any], expectation: typing.Any, tmp_path: pathlib.Path):
    with expectation:
        path = tmp_path.joinpath(f"config.{format}")

        if format == "string":
            config = Config.from_file(str(path.with_suffix(".toml")))

        else:
            config = Config.from_file(path)

        dump = {key: value for key, value in config.model_dump(mode="json").items() if key in dictionary}

        assert dictionary == dump


def test_from_environment_variables(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as mp:
        mp.setenv("TMO_database__dialect", "sqlite")
        mp.setenv("TMO_database__path", "/dev/null")

        m = Config()
        assert isinstance(m.database, Sqlite)
        assert m.database.dialect == "sqlite"
        assert m.database.path.as_posix() == "/dev/null"


def test_memory():
    m = Config(database={"dialect": "memory"})  # type: ignore[arg-type]

    assert isinstance(m.database, Memory)
    assert m.database.dialect == "memory" and m.database.path is None


def test_patch():
    m = Config()
    assert m.api.port == 8000
    port = random.randint(1000, 60000)

    with m.patch(api={"port": port}):
        assert m.api.port == port


class TestLoad:
    def test_name_validation(self, faker: Faker):
        names = {faker.first_name(): faker.last_name() for _ in range(5)}
        Load.model_validate({"names": {"default": "default", **names}})

    def test_name_validation_fails(self, faker: Faker):
        with pytest.raises(ValueError):
            assert Load.model_validate({"names": {faker.first_name(): faker.last_name()}})


class TestFrontend:
    size: int = 6

    def test_color_validation(self, faker: Faker):
        colors = {faker.first_name(): faker.color() for _ in range(self.size)}

        assert Frontend.model_validate({"colors": colors})

    def test_color_validation_fails(self, faker: Faker):
        colors = {faker.first_name(): "#ffffff", faker.first_name(): "#ffffff"}

        with pytest.raises(ValueError, match="must be unique"):
            Frontend.model_validate({"colors": colors})

    def test_dependent_validation(self, faker: Faker):
        dependents = {
            (name := faker.first_name()): [name] + [faker.first_name() for _ in range(self.size)],
            (name := faker.first_name()): [name],
        }
        assert Frontend.model_validate({"dependents": dependents})

    def test_dependent_validation_fails(self, faker: Faker):
        dependents = {faker.first_name(): [faker.first_name() for _ in range(self.size)]}

        with pytest.raises(ValueError):
            Frontend.model_validate({"dependents": dependents})
