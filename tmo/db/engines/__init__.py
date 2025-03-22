import logging
import sys
import typing

from sqlalchemy import Engine
from sqlmodel import SQLModel

from ... import config
from ...config import Memory, Postgres, Sqlite
from ..highlight import attach_handler
from ..models import Bill, BillSubscriberLink, Charge, Detail, Subscriber
from ._postgres import init as _init_postgres
from ._sqlite import init as _init_sqlite

logging.basicConfig()


def start_engine(connect_args: dict[str, typing.Any] | None = None) -> Engine:
    connect_args = connect_args or {}

    match config.database:
        case Sqlite() | Memory():
            engine = _init_sqlite(config.database, connect_args=connect_args)

        case Postgres():
            engine = _init_postgres(config.database, connect_args=connect_args)

        case _:
            logging.getLogger("uvicorn.error").error("Could not match the database type: %s", type(config.database))
            sys.exit(1)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    if config.database.echo:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        attach_handler()

    SQLModel.metadata.create_all(engine)

    return engine


__all__ = ["Bill", "BillSubscriberLink", "Charge", "Detail", "Subscriber"]
