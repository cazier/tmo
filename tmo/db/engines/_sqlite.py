import pathlib
import typing

from sqlalchemy import Engine
from sqlmodel import create_engine


def init(*, path: str | None = None, memory: bool = False, clear: bool = False, **_: typing.Any) -> Engine:
    if bool(path) == memory:
        raise RuntimeError("Cannot create a sqlite database in memory AND at a specific path.")

    url = "sqlite://"

    if path:
        _path = pathlib.Path.cwd().joinpath(path)

        if clear:
            _path.unlink(missing_ok=True)

        url = f"{url}/{_path.resolve()}"

    engine = create_engine(url)

    return engine
