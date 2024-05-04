import pathlib
import tomllib
import typing

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator

_file = pathlib.Path.cwd().joinpath("config.toml")
_config = tomllib.loads(_file.read_text(encoding="utf8"))

database: dict[str, str | bool | None] = _config["database"]

load: dict[str, dict[str, str]] = _config["load"]

api: dict[str, bool] = _config["api"]
frontend: dict[str, dict[str, str | list[str]]] = _config["frontend"]

convert: dict[str, dict[str, str]] = _config["convert"]


class _Database(BaseModel):
    dialect: typing.Literal["sqlite", "postgres"]
    path: pathlib.Path
    echo: bool = False
    clear: bool = False

    def keys(self) -> typing.Iterator[str]:
        # TODO: Implement **kwarg methods
        return self.model_fields.keys()


class _Load(BaseModel):
    names: dict[typing.Literal["default"] | str, str] = Field(default_factory=dict)

    @field_validator("names", mode="before")
    @classmethod
    def check_names(cls, values: dict[str, str]):
        if values and "default" not in values:
            raise ValueError("default must be supplied in the load-names map")

        return values


class _Frontend(BaseModel):
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


class _Api(BaseModel):
    debug: bool = False
    port: int = 8000
    host: IPvAnyAddress = Field(default="0.0.0.0", validate_default=True)


class Config(BaseModel):
    database: _Database
    load: _Load = Field(default_factory=_Load)
    frontend: _Frontend = Field(default_factory=_Frontend)
    api: _Api = Field(default_factory=_Api)

    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> "Config":
        """Load configuration data from a file (there is support for toml and json files) and initialize a
        config object.

        Args:
            path (pathlib.Path | str): path to the file

        Raises:
            TypeError: If the file type cannot be automatically determined or is not supported.

        Returns:
            Config: An instance of the Config class containing the loaded configuration data
        """
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
