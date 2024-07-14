import contextlib
import pathlib
import typing

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict

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


class CustomEnvSource(EnvSettingsSource):
    def explode_env_vars(
        self, field_name: str, field: FieldInfo, env_vars: typing.Mapping[str, str | None]
    ) -> dict[str, typing.Any]:
        data = super().explode_env_vars(field_name, field, env_vars)
        data.setdefault("database", {})
        data["database"].setdefault("dialect", "memory")
        return data


class Config(Sentinel, BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="TMO_")

    database: Sqlite | Postgres = Field(discriminator="dialect")
    load: Load = Field(default_factory=Load)
    frontend: Frontend = Field(default_factory=Frontend)
    api: Api = Field(default_factory=Api)

    @classmethod
    def settings_customise_sources(cls, settings_cls: type[BaseSettings], **kwargs) -> tuple[PydanticBaseSettingsSource, ...]:
        kwargs["env_settings"] = CustomEnvSource(settings_cls)
        return super().settings_customise_sources(settings_cls, **kwargs)

    # @model_validator(mode='before')
    # @classmethod
    # def _database(cls, data: T | typing.Any) -> T:
    #     breakpoint()
    #     if isinstance(data, dict):
    #         data.setdefault('database', {})
    #         data['database'].setdefault('dialect', 'memory')
    #         return data

    #     raise NotImplementedError("Implementing config is currently only possible from a dictionary/JSON object.")

    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> typing.Self:
        # pylint: disable=import-outside-toplevel
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

    @contextlib.contextmanager
    def patch(self, **patches: dict[str, typing.Any]) -> typing.Generator[None, None, None]:
        original = self.model_dump(mode="json")
        with self.update_self():
            self.model_validate(merge_dict(original, patches))

        yield

        with self.update_self():
            self.model_validate(original, strict=True)


config = None  # Config()
