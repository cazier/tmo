from sqlalchemy import URL, Engine
from sqlmodel import create_engine

from tmo.config import Postgres


def init(config: Postgres) -> Engine:
    url = URL.create(
        "psycopg",
        username=config.username,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )

    engine = create_engine(url)

    return engine
