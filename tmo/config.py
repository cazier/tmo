import contextlib
import pathlib
import typing

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .lib.sentinel import Sentinel

T = typing.TypeVar("T", bound=dict[str, typing.Any])


class Sqlite(BaseModel, validate_assignment=True):
    dialect: typing.Literal["memory", "sqlite"]
    echo: bool = False
    clear: bool = False

    path: pathlib.Path | None = None


class Postgres(BaseModel, validate_assignment=True):
    dialect: typing.Literal["postgres"]
    echo: bool = False
    clear: bool = False

    username: str
    password: str
    database: str
    host: str
    port: int


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


class Config(Sentinel, BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="TMO_")

    database: Sqlite | Postgres = Field(default_factory=Sqlite)
    load: Load = Field(default_factory=Load)
    frontend: Frontend = Field(default_factory=Frontend)
    api: Api = Field(default_factory=Api)

    @model_validator(mode="before")
    @classmethod
    def _database(cls, data: T | None = None) -> T:
        # TODO: it's annoying to have to set this here manually instead of pydantic managing it all
        if data is None:
            data = {"database": {"dialect": "sqlite"}}
        if "database" in data:
            data["database"].setdefault("dialect", "sqlite")
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

        return cls.model_validate(parse(path.read_text(encoding="utf8")))

    @staticmethod
    def _nested_merge(original: T, update: T) -> T:
        def _recurse(combined, new, _return=True):  # type: ignore
            for key, value in new.items():
                if isinstance(value, dict):
                    _recurse(combined.setdefault(key, {}), value, _return=False)  # type: ignore
                else:
                    combined[key] = value

            if _return:
                return combined

            return

        return _recurse(_recurse({}, original), update)  # type: ignore

    @contextlib.contextmanager
    def patch(self, **patches: dict[str, typing.Any]) -> typing.Generator[None, None, None]:
        original = self.model_dump(mode="json")
        with self.update_self():
            self.model_validate(self._nested_merge(original, patches))

        yield

        with self.update_self():
            self.model_validate(original, strict=True)


config = Config()
