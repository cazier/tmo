from typing import Generator, Sequence

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from tmo.config import api
from tmo.db.engines import engine
from tmo.db.models import Bill, Subscriber

app = FastAPI(debug=api["debug"])


def _get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@app.get("/bill/")
def get_bills(*, session: Session = Depends(_get_session)) -> Sequence[Bill]:
    bills = session.exec(select(Bill)).all()
    return bills


@app.get("/subscriber/")
def get_subscribers(*, session: Session = Depends(_get_session)) -> Sequence[Subscriber]:
    subscribers = session.exec(select(Subscriber)).all()
    return subscribers
