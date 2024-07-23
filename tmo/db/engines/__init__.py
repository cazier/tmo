import logging
import sys

from sqlalchemy import Engine
from sqlmodel import SQLModel

from tmo import config
from tmo.config import Memory, Postgres, Sqlite
from tmo.db.highlight import attach_handler
from tmo.db.models import Bill, BillSubscriberLink, Charge, Detail, Subscriber

from ._postgres import init as _init_postgres
from ._sqlite import init as _init_sqlite

logging.basicConfig()


def start_engine() -> Engine:
    match config.database:
        case Sqlite() | Memory():
            engine = _init_sqlite(config.database)

        case Postgres():
            engine = _init_postgres(config.database)

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
