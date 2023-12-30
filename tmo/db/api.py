import datetime
from typing import Any, Generator, Sequence, cast

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.engine.result import TupleResult
from sqlalchemy.orm import joinedload
from sqlmodel import Session, and_, func, select

from tmo.db.engines import engine
from tmo.db.models import (
    Bill,
    BillRead,
    BillReadWithSubscribers,
    Detail,
    MonthValidator,
    Subscriber,
    SubscriberRead,
    SubscriberReadWithDetails,
    SubscribersRead,
    _Subscriber_Bill_Link,
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


# @api.get("/month/{id}", responses=_additional_responses)
# def get_month(*, id: int, session: Session = Depends(_session)) -> Month:
#     month = session.get(Bill, id)
#     if month is None:
#         raise HTTPException(status_code=404, detail="Month could not be found")

#     data = session.exec(
#         select(Subscriber, Detail)
#         .select_from(Bill)
#         .join(_Subscriber_Bill_Link, Bill.id == _Subscriber_Bill_Link.bill_id)
#         .join(Subscriber, _Subscriber_Bill_Link.subscriber_id == Subscriber.id)
#         .join(Detail, and_(Subscriber.id == Detail.subscriber_id, Bill.id == Detail.bill_id), isouter=True)
#         .where(Bill.id == id),
#     ).all()

#     return Month(
#         id=month.id,
#         date=month.date,
#         subscribers=[SubscriberBill(subscriber=subscriber, detail=detail) for subscriber, detail in data],
#     )


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


@router.get("/month/current", responses=_additional_responses)
async def get_bill_by_current(*, session: Session = Depends(_session)) -> MonthValidator:
    today = datetime.datetime.today()
    today = datetime.datetime(2023, 5, 4)
    return await get_bill_by_date(year=today.year, month=today.month, session=session)


@router.get("/month/{year}/{month}", responses=_additional_responses)
async def get_bill_by_date(*, year: int, month: int, session: Session = Depends(_session)) -> MonthValidator:
    # pylint: disable=not-callable
    id = session.exec(
        select(Bill.id).where(
            and_(
                func.extract("year", Bill.date) == year,
                func.extract("month", Bill.date) == month,
            )
        )
    ).first()

    if id is None:
        raise HTTPException(status_code=404, detail="No month data could be found")

    return await get_bill_by_id(id=id, session=session)


@router.get("/month/{id}", responses=_additional_responses)
async def get_bill_by_id(*, id: int, session: Session = Depends(_session)) -> MonthValidator:
    data = cast(
        TupleResult[tuple[Bill, Subscriber, Detail]],
        session.exec(
            select(Bill, Subscriber, Detail)
            .options(joinedload(Bill.charges))
            .join(_Subscriber_Bill_Link, Bill.id == _Subscriber_Bill_Link.bill_id)
            .join(Subscriber, _Subscriber_Bill_Link.subscriber_id == Subscriber.id)
            .join(
                Detail,
                and_(
                    Subscriber.id == Detail.subscriber_id,
                    Bill.id == Detail.bill_id,
                ),
                isouter=True,
            )
            .where(Bill.id == id)
        ).unique(),
    ).all()

    if data is None:
        raise HTTPException(status_code=404, detail="No month data could be found")

    return MonthValidator.stuff_data(data)
