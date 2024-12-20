import typing

from sqlalchemy import URL, Engine
from sqlmodel import create_engine

from tmo.config import Postgres


def init(config: Postgres, connect_args: dict[str, typing.Any] | None = None) -> Engine:
    connect_args = connect_args or {}

    url = URL.create(
        "postgresql+psycopg",
        username=config.username,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )

    engine = create_engine(url, connect_args=connect_args)

    return engine
