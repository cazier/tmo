import datetime
from typing import Any, Generator, Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlmodel import Session, and_, func, select

from tmo.db.engines import engine
from tmo.db.models import (
    Bill,
    BillRead,
    BillReadWithSubscribers,
    BillRender,
    Detail,
    Subscriber,
    SubscriberRead,
    SubscriberReadWithDetails,
    SubscribersRead,
)


def _session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


class Error(BaseModel):
    error: str


class DatabaseDetails(BaseModel):
    bills: int
    subscribers: int


_additional_responses: dict[int, dict[str, Any]] = {
    404: {"model": Error, "description": "No item(s) matching the query could be found."}
}

router = APIRouter(prefix="/api", responses=_additional_responses)


@router.get("/details")
async def get_details(*, session: Session = Depends(_session)) -> DatabaseDetails:
    """Get details for the database, including numbers of records and date ranges, etc."""
    # pylint: disable=not-callable
    return session.exec(
        select(
            select(func.count(Bill.id)).scalar_subquery().label("bills"),
            select(func.count(Subscriber.id)).scalar_subquery().label("subscribers"),
        )
    ).first()


@router.get("/bills")
async def get_bills(
    *, start: int = 0, count: int = Query(default=100, let=100), session: Session = Depends(_session)
) -> Sequence[BillRead]:
    bills = session.exec(select(Bill).order_by(Bill.id).offset(start).limit(count)).all()
    return bills


@router.get("/bill/{id}", responses=_additional_responses, response_model=BillReadWithSubscribers)
async def get_bill(*, id: int, session: Session = Depends(_session)) -> Bill:
    bill = session.get(Bill, id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill could not be found")
    return bill


@router.get("/subscribers")
async def get_subscribers(
    *, start: int = 0, count: int = Query(default=100, let=100), session: Session = Depends(_session)
) -> Sequence[SubscribersRead]:
    subscribers = session.exec(select(Subscriber).order_by(Subscriber.id).offset(start).limit(count)).all()
    return subscribers


@router.get("/subscriber/{id}", responses=_additional_responses)
async def get_subscriber(*, id: int, session: Session = Depends(_session)) -> SubscriberRead:
    subscriber = session.exec(select(Subscriber).where(Subscriber.id == id)).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber could not be found")
    return subscriber


@router.get("/subscriber/{id}/charges/{charge_id}", responses=_additional_responses)
async def get_subscriber_charge(
    *, id: int, charge_id: int, session: Session = Depends(_session)
) -> SubscriberReadWithDetails:
    subscriber = session.exec(
        select(Subscriber, Detail).where(Subscriber.id == id).where(Detail.bill_id == charge_id)
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber could not be found")
    return subscriber


# @router.get("/month/current", responses=_additional_responses)
# @router.get("/month/{year}/{month}", responses=_additional_responses)
# @router.get("/month/{id}", responses=_additional_responses)
# async def get_bill(
#     *,
#     year: Optional[int] = None,
#     month: Optional[int] = None,
#     id: Optional[int] = None,
#     session: Session = Depends(_session)
# ) -> MonthValidator:


@router.get("/month/current", responses=_additional_responses)
async def get_bill_by_current(*, render: bool = False, session: Session = Depends(_session)) -> BillRender:
    return await _get_bill(session=session, render=render, id=None, year=None, month=None)


@router.get("/month/{year}/{month}", responses=_additional_responses)
async def get_bill_by_date(
    *, year: int, month: int, render: bool = False, session: Session = Depends(_session)
) -> BillRender:
    return await _get_bill(year=year, month=month, session=session, render=render, id=None)


@router.get("/month/{id}", responses=_additional_responses)
async def get_bill_by_id(*, id: int, render: bool = False, session: Session = Depends(_session)) -> BillRender:
    return await _get_bill(id=id, session=session, render=render, year=None, month=None)


async def _get_bill(
    session: Session, render: bool, year: Optional[int], month: Optional[int], id: Optional[int]
) -> Bill:
    if id is None and month is None and year is None:
        today = datetime.datetime.today()

        year = today.year
        month = today.month

    if year and month:
        id = session.exec(
            select(Bill.id).where(
                and_(
                    # pylint: disable=not-callable
                    func.extract("year", Bill.date) == year,
                    func.extract("month", Bill.date) == month,
                )
            )
        ).first()

        if id is None:
            raise HTTPException(status_code=404, detail="No month data could be found")

    data = (
        session.exec(
            select(Bill)
            .options(
                joinedload(Bill.charges),
                joinedload(Bill.subscribers).joinedload(Subscriber.details.and_(Detail.bill_id == Bill.id)),
            )
            .where(Bill.id == id)
        )
        .unique()
        .first()
    )

    if data is None:
        raise HTTPException(status_code=404, detail="No month data could be found")

    return data
