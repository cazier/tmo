import pathlib
import tomllib

_file = pathlib.Path.cwd().joinpath("config.toml")
_config = tomllib.loads(_file.read_text(encoding="utf8"))

# @dataclasses.dataclass
# class Config:
#     database: collections.namedtuple('database', )

database: dict[str, str | bool | None] = _config["database"]

load: dict[str, dict[str, str]] = _config["load"]

api: dict[str, bool] = _config["api"]
frontend: dict[str, dict[str, str | list[str]]] = _config["frontend"]

convert: dict[str, dict[str, str]] = _config["convert"]
