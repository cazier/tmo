import contextlib
import pathlib
import typing

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, PrivateAttr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    def check_names(cls, values: dict[str, str]):
        if values and "default" not in values:
            raise ValueError("default must be supplied in the load-names map")

        return values


class Frontend(BaseModel, validate_assignment=True):
    colors: dict[str, str] = Field(default_factory=dict)
    dependents: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("colors", mode="before")
    @classmethod
    def check_colors(cls, values: dict[str, str]) -> dict[str, str]:
        colors = set()
        for color in values.values():
            if color in colors:
                raise ValueError("Colors must be unique.")

            colors.add(color)

        return values

    @field_validator("dependents", mode="before")
    @classmethod
    def check_dependents(cls, values: dict[str, list[str]]) -> dict[str, list[str]]:
        for payer, dependent in values.items():
            if payer not in dependent:
                raise ValueError("The dependent list MUST include the payer themselves.")

        return values


class Api(BaseModel, validate_assignment=True):
    debug: bool = False
    port: int = 8000
    host: IPvAnyAddress = Field(default="0.0.0.0", validate_default=True)


class _Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="TMO_")

    database: Sqlite | Postgres = Field(default_factory=Sqlite)
    load: Load = Field(default_factory=Load)
    frontend: Frontend = Field(default_factory=Frontend)
    api: Api = Field(default_factory=Api)

    @model_validator(mode="before")
    @classmethod
    def _database(cls, data: dict[str, dict[str, typing.Any]] | None = None):
        # TODO: it's annoying to have to set this here manually instead of pydantic managing it all
        if not data:
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


class Config(_Config):
    model_config = ConfigDict(frozen=True)
    _data: _Config = PrivateAttr(default_factory=_Config)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = self.model_copy(deep=True)

    def __getattribute__(self, key: str):
        if key in super().model_fields or key == "model_dump":
            return object.__getattribute__(self._data, key)

        return object.__getattribute__(self, key)

    def __repr__(self) -> str:
        fields = ", ".join(f"{field}={repr(getattr(self, field))}" for field in self.model_fields)
        return f"Config({fields})"

    def __str__(self) -> str:
        return self.__repr__()

    def __rich__(self) -> str:
        return self.__repr__()

    def from_file(self, path: pathlib.Path | str | None = None) -> typing.Self:
        __doc__ = _Config.__doc__

        # THIS IS REAL HACKY, but lets us use this as a classmethod as well as an instancemethod...
        if path is None:
            return Config().from_file(self)

        self._data = super().from_file(path)
        return self

    @contextlib.contextmanager
    def patch(self, **patches: dict[str, typing.Any]) -> typing.Generator[typing.Self, None, None]:
        original = self._data.model_dump(mode="json")
        self._data = super().model_validate({**original, **patches})

        yield

        self._data = super().model_validate(original, strict=True)


config = Config()
