# mypy: disable-error-code="return-value"

import datetime

from fastapi import APIRouter, Query
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select

from ..db.models import Bill, Detail, Subscriber
from ..dependencies import SessionDependency
from ..lib.utilities import cast_as_qa
from ..web2.exceptions import APIException
from .responses import ReadBill, ReadBillSubscribersChargesDetail, ReadBillSubscriberTotalsCharges

router = APIRouter(prefix="/bill")


@router.get("")
async def get_bills(
    *, start: int = 0, count: int = Query(default=100, let=100), session: SessionDependency
) -> list[ReadBill]:
    bills = session.exec(select(Bill).order_by(col(Bill.id).asc()).offset(start).limit(count)).all()
    return bills


@router.get("/previous-ids")
async def get_previous_ids(
    *,
    before: datetime.date = Query(default_factory=datetime.date.today),
    count: int = Query(default=2, let=5),
    session: SessionDependency,
) -> list[int]:
    return session.exec(select(Bill.id).where(Bill.date <= before).limit(count).order_by(col(Bill.date).desc())).all()


async def _get_bill(*, id: int, session: Session) -> Bill | None:
    return (
        session.exec(
            select(Bill)
            .where(Bill.id == id)
            .options(
                joinedload(cast_as_qa(Bill.charges)),
                joinedload(cast_as_qa(Bill.subscribers)).joinedload(
                    cast_as_qa(Subscriber.details).and_(col(Detail.bill_id) == id)
                ),
            )
        )
        .unique()
        .first()
    )


@router.get("/{id}")
async def get_bill_id(*, id: int, session: SessionDependency) -> ReadBillSubscriberTotalsCharges:
    bill = await _get_bill(id=id, session=session)

    if not bill:
        raise APIException(status_code=404, detail="Bill could not be found")
    return bill


@router.get("/{id}/detailed", include_in_schema=False)
async def get_bill_detailed(*, id: int, session: SessionDependency) -> ReadBillSubscribersChargesDetail:
    bill = await _get_bill(id=id, session=session)

    if not bill:
        raise APIException(status_code=404, detail="Bill could not be found")
    return bill


@router.get("/{year}/{month}")
async def get_bill_date(*, year: int, month: int, session: SessionDependency) -> ReadBillSubscriberTotalsCharges:
    subquery = (
        select(Bill.id)
        .where(Bill.date >= datetime.date(year, month, 1))
        .order_by(col(Bill.date).asc())
        .limit(1)
        .scalar_subquery()
    )

    bill = (
        session.exec(
            select(Bill)
            .where(Bill.id == subquery)
            .order_by(col(Bill.date).asc())
            .limit(1)
            .options(
                joinedload(cast_as_qa(Bill.charges)),
                joinedload(cast_as_qa(Bill.subscribers)).joinedload(
                    cast_as_qa(Subscriber.details).and_(col(Detail.bill_id) == subquery)
                ),
            )
        )
        .unique()
        .first()
    )

    if not bill:
        raise APIException(status_code=404, detail="Bill could not be found")
    return bill
