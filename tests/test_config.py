import contextlib
import json
import pathlib
import random
import tomllib
import typing

import faker
import pytest

from tmo.config import Config, Frontend, Load


@pytest.fixture(scope="session")
def gen_data() -> str:
    return f"""
[database]
dialect = "sqlite"
path = "db.sqlite3"
echo = {random.choice(('true', 'false'))}
clear = {random.choice(('true', 'false'))}
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
def test_from_file(
    format: str, dictionary: dict[str, typing.Any], expectation: typing.Any, tmp_path: pathlib.Path
) -> None:
    with expectation:
        path = tmp_path.joinpath(f"config.{format}")

        if format == "string":
            path = str(path.with_suffix(".toml"))

        config = Config.from_file(path)
        dump = {key: value for key, value in config.model_dump(mode="json").items() if key in dictionary}

        assert dictionary == dump


def test_from_environment_variables(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as mp:
        mp.setenv("TMO_database__dialect", "sqlite")
        mp.setenv("TMO_database__path", "/dev/null")

        c = Config()
        assert c.database.dialect == "sqlite"
        assert c.database.path.as_posix() == "/dev/null"


def test_memory():
    c = Config(database=dict(dialect="memory"))
    assert c.database.dialect == "memory"
    assert c.database.path is None


def test_patch():
    c = Config()
    assert c.api.port == 8000
    port = random.randint(1000, 60000)

    with c.patch(api=dict(port=port)):
        assert c.api.port == port


class TestLoad:
    def test_name_validation(self, faker: faker.Faker) -> None:
        names = {faker.first_name(): faker.last_name() for _ in range(5)}
        Load.model_validate({"names": {"default": "default", **names}})

    def test_name_validation_fails(self, faker: faker.Faker) -> None:
        with pytest.raises(ValueError):
            assert Load.model_validate({"names": {faker.first_name(): faker.last_name()}})


class TestFrontend:
    size: int = 6

    def test_color_validation(self, faker: faker.Faker) -> None:
        colors = {faker.first_name(): faker.color() for _ in range(self.size)}

        assert Frontend.model_validate({"colors": colors})

    def test_color_validation_fails(self, faker: faker.Faker) -> None:
        colors = {faker.first_name(): "#ffffff", faker.first_name(): "#ffffff"}

        with pytest.raises(ValueError, match="must be unique"):
            Frontend.model_validate({"colors": colors})

    def test_dependent_validation(self, faker: faker.Faker) -> None:
        dependents = {
            (name := faker.first_name()): [name] + [faker.first_name() for _ in range(self.size)],
            (name := faker.first_name()): [name],
        }
        assert Frontend.model_validate({"dependents": dependents})

    def test_dependent_validation_fails(self, faker: faker.Faker) -> None:
        dependents = {faker.first_name(): [faker.first_name() for _ in range(self.size)]}

        with pytest.raises(ValueError):
            Frontend.model_validate({"dependents": dependents})
