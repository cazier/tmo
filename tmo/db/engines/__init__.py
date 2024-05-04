import logging

from sqlmodel import SQLModel

from tmo.config import database
from tmo.db.highlight import attach_handler
from tmo.db.models import Bill, BillSubscriberLink, Charge, Detail, Subscriber

from ._postgres import init as _init_postgres
from ._sqlite import init as _init_sqlite

logging.basicConfig()

match database.pop("dialect"):
    case "sqlite":
        engine = _init_sqlite(**database)  # type: ignore[arg-type]

    case "postgres":
        engine = _init_postgres(**database)  # type: ignore[arg-type]

    case _:
        import sys

        sys.exit(1)

if database.get("echo"):
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    attach_handler()

# This just exists to prevent linters from removing unused imports
# pylint: disable-next=pointless-statement
(Bill, BillSubscriberLink, Charge, Detail, Subscriber)

SQLModel.metadata.create_all(engine)
