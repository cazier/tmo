import datetime
from typing import Sequence

from fastapi import APIRouter, HTTPException, Query
import pydantic
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ..dependencies import SessionDependency
from ..db.models.tables import *



router = APIRouter(prefix="/bill")


class ReadBill(BillScalar):
    id: int


class ReadSubscribersDetail(SubscriberScalar):
    id: int
    details: DetailScalar

    @pydantic.field_validator("details", mode="before")
    @classmethod
    def get_entry(cls, data: DetailScalar):
        if len(data) != 1:
            raise ValueError("Data must only contain one detail entry")
        return data[0]


class ReadBillWithSubscriberDetail(ReadBill):
    id: int
    charges: list[ChargeScalar]
    subscribers: list[ReadSubscribersDetail]


@router.get("")
async def get_bills(*, start: int = 0, count: int = Query(default=100, let=100), session: SessionDependency) -> Sequence[ReadBill]:
    bills = session.exec(select(Bill).order_by(Bill.id).offset(start).limit(count)).all()
    return bills


@router.get("/{id}")
async def get_bill(*, id: int, session: SessionDependency) -> ReadBillWithSubscriberDetail:
    bill = (
        session.exec(
            select(Bill)
            .where(Bill.id == id)
            .options(
                joinedload(Bill.charges),
                joinedload(Bill.subscribers).joinedload(Subscriber.details.and_(Detail.bill_id == id))
            )
        )
        .unique()
        .first()
    )

    if not bill:
        raise HTTPException(status_code=404, detail="Bill could not be found")
    return bill

@router.get("/{year}/{month}")
async def get_bill(*, year: int, month: int, session: SessionDependency) -> ReadBillWithSubscriberDetail:
    subquery = select(Bill.id).where(Bill.date >= datetime.date(year, month, 1)).order_by(Bill.date.asc()).limit(1).scalar_subquery()

    bill = (
        session.exec(
            select(Bill)
            .where(Bill.id == subquery)
            .order_by(Bill.date.asc())
            .limit(1)
            .options(
                joinedload(Bill.charges),
                joinedload(Bill.subscribers).joinedload(Subscriber.details.and_(Detail.bill_id == subquery))
            )
        )
        .unique()
        .first()
    )

    if not bill:
        raise HTTPException(status_code=404, detail="Bill could not be found")
    return bill

