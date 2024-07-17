import pathlib

from sqlalchemy import Engine
from sqlmodel import create_engine

from tmo.config import Memory, Sqlite


def init(config: Sqlite | Memory) -> Engine:
    url = "sqlite://"

    if config.path:
        path = pathlib.Path.cwd().joinpath(config.path)

        if config.clear:
            path.unlink(missing_ok=True)

        url = f"{url}/{path.resolve()}"

    engine = create_engine(url)

    return engine
