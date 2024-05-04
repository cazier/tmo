import contextlib
import json
import pathlib
import random
import tomllib
import typing

import faker
import pytest

from tmo.config import Config, _Frontend, _Load


@pytest.fixture
def gen_data() -> str:
    return f"""
[database]
dialect = "{random.choice(('sqlite', 'postgres'))}"
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

        c = Config.from_file(path)

        for key, value in dictionary.items():
            assert value == c.model_dump(mode="json")[key]


class TestLoad:
    def test_name_validation(self, faker: faker.Faker) -> None:
        names = {faker.first_name(): faker.last_name() for _ in range(5)}
        _Load.model_validate({"names": {"default": "default", **names}})

    def test_name_validation_fails(self, faker: faker.Faker) -> None:
        with pytest.raises(ValueError):
            assert _Load.model_validate({"names": {faker.first_name(): faker.last_name()}})


class TestFrontend:
    size: int = 6

    def test_color_validation(self, faker: faker.Faker) -> None:
        colors = {faker.first_name(): faker.color() for _ in range(self.size)}

        assert _Frontend.model_validate({"colors": colors})

    def test_color_validation_fails(self, faker: faker.Faker) -> None:
        colors = {faker.first_name(): "#ffffff", faker.first_name(): "#ffffff"}

        with pytest.raises(ValueError, match="must be unique"):
            _Frontend.model_validate({"colors": colors})

    def test_dependent_validation(self, faker: faker.Faker) -> None:
        dependents = {
            (name := faker.first_name()): [name] + [faker.first_name() for _ in range(self.size)],
            (name := faker.first_name()): [name],
        }
        assert _Frontend.model_validate({"dependents": dependents})

    def test_dependent_validation_fails(self, faker: faker.Faker) -> None:
        dependents = {faker.first_name(): [faker.first_name() for _ in range(self.size)]}

        with pytest.raises(ValueError):
            _Frontend.model_validate({"dependents": dependents})
