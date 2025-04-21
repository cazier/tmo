import contextlib
import ipaddress
import pathlib
import typing

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

T = dict[str, "T"]


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
    swap: dict[str, dict[str, str]] = Field(default_factory=dict)

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
    host: IPvAnyAddress = Field(default=ipaddress.IPv4Address("0.0.0.0"))


class Fetch(BaseModel, validate_assignment=True):
    username: str
    password: str
    totp_secret: str = ""


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="TMO_")

    database: Memory | Sqlite | Postgres = Field(default_factory=Memory)
    load: Load = Field(default_factory=Load)
    frontend: Frontend = Field(default_factory=Frontend)
    api: Api = Field(default_factory=Api)
    fetch: Fetch | None = None

    def __set(self, new: dict[str, typing.Any]) -> None:
        model = self.model_validate(new)

        for name in type(self).model_fields:
            setattr(self, name, getattr(model, name))

    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> "Config":
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

        config.__set(parse(path.read_text(encoding="utf8")))
        return config

    @contextlib.contextmanager
    def patch(self, **patches: dict[str, typing.Any]) -> typing.Generator[None, None, None]:
        original = self.model_dump()
        self.__set(self.model_copy(update=patches, deep=True).model_dump(warnings="none"))

        yield

        self.__set(original)


config = Config()
