import logging

from sqlmodel import SQLModel

from tmo.config import database
from tmo.db.models import Bill, Charges, Statistics, Subscriber, _Charges_Statistics_Link, _Subscriber_Bill_Link

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

# This just exists to prevent linters from removing unused imports
# pylint: disable-next=pointless-statement
(Bill, Charges, Statistics, Subscriber, _Charges_Statistics_Link, _Subscriber_Bill_Link)

SQLModel.metadata.create_all(engine)
