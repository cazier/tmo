import contextlib
import pathlib
import typing

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .lib.sentinel import Sentinel

T = dict[str, "T"]


def merge_dict(original: T, update: T) -> T:
    def _recurse(combined: T, new: T) -> None:
        for key, value in new.items():
            if isinstance(value, dict):
                _recurse(combined=combined.setdefault(key, {}), new=value)
            else:
                combined[key] = value

    result: T = {}
    _recurse(result, original)
    _recurse(result, update)
    return result


class _Databases(BaseModel, validate_assignment=True):
    echo: bool = False
    clear: bool = False


class Sqlite(_Databases):
    dialect: typing.Literal["sqlite"] = "sqlite"

    path: pathlib.Path


class Memory(_Databases):
    dialect: typing.Literal["memory"] = "memory"

    path: None = None


class Postgres(_Databases):
    dialect: typing.Literal["postgres"] = "postgres"

    username: str
    password: str
    database: str
    host: str
    port: int = 5432


class Load(BaseModel, validate_assignment=True):
    numbers: dict[str, str] = Field(default_factory=dict)
    names: dict[typing.Literal["default"] | str, str] = Field(default_factory=dict)

    @field_validator("names", mode="before")
    @classmethod
    def check_names(cls, values: T) -> T:
        if values and "default" not in values:
            raise ValueError("default must be supplied in the load-names map")

        return values


class Frontend(BaseModel, validate_assignment=True):
    colors: dict[str, str] = Field(default_factory=dict)
    dependents: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("colors", mode="before")
    @classmethod
    def check_colors(cls, values: T) -> T:
        colors = set()
        for color in values.values():
            if color in colors:
                raise ValueError("Colors must be unique.")

            colors.add(color)

        return values

    @field_validator("dependents", mode="before")
    @classmethod
    def check_dependents(cls, values: T) -> T:
        for payer, dependent in values.items():
            if payer not in dependent:
                raise ValueError("The dependent list MUST include the payer themselves.")

        return values


class Api(BaseModel, validate_assignment=True):
    debug: bool = False
    port: int = 8000
    host: IPvAnyAddress = Field(default="0.0.0.0", validate_default=True)


class Fetch(BaseModel, validate_assignment=True):
    username: str
    password: str
    totp_secret: str = ""


class Config(Sentinel, BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="TMO_")

    database: Memory | Sqlite | Postgres = Field(default=Memory(), discriminator="dialect")
    load: Load = Field(default_factory=Load)
    frontend: Frontend = Field(default_factory=Frontend)
    api: Api = Field(default_factory=Api)
    fetch: Fetch | None = None

    @model_validator(mode="before")
    @classmethod
    def _database(cls, data: T | typing.Any) -> T:
        # TODO, this continues to get squirrely...
        if not data:
            data = {"database": {"dialect": "memory"}}

        if data["database"].get("dialect") != "postgres" and data["database"].get("path") is not None:
            data["database"]["dialect"] = "sqlite"  # type: ignore[assignment]

        return data

    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> typing.Self:
        if isinstance(path, str):
            path = pathlib.Path(path).resolve()

        match path.suffix:
            case ".toml":
                import tomllib

                parse = tomllib.loads

            case ".json":
                import json

                parse = json.loads

            case _:
                raise TypeError("Could not automatically determine the input file type")

        with cls.update_sentinel():
            return cls.model_validate(parse(path.read_text(encoding="utf8")))

    @contextlib.contextmanager
    def patch(self, **patches: dict[str, typing.Any]) -> typing.Generator[None, None, None]:
        original = self.model_dump(mode="json")
        with self.update_sentinel():
            self.model_validate(merge_dict(original, patches))

        yield

        with self.update_sentinel():
            self.model_validate(original, strict=True)


config = Config()
