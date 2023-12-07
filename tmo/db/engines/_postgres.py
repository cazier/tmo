import typing

from sqlalchemy import URL, Engine
from sqlmodel import create_engine


def init(
    *,
    database: str,
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    port: int | None = None,
    **_: typing.Any
) -> Engine:
    url = URL.create(
        "psycopg",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    engine = create_engine(url)

    return engine
