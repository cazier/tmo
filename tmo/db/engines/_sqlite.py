import pathlib
import typing

from sqlalchemy import Engine
from sqlmodel import create_engine

from ...config import Memory, Sqlite


def init(config: Sqlite | Memory, connect_args: dict[str, typing.Any] | None = None) -> Engine:
    connect_args = connect_args or {}
    pool = connect_args.pop("pool", None)

    url = "sqlite://"

    if config.path:
        path = pathlib.Path.cwd().joinpath(config.path)

        if config.clear:
            path.unlink(missing_ok=True)

        url = f"{url}/{path.resolve()}"

    engine = create_engine(url, connect_args=connect_args, poolclass=pool)

    return engine
