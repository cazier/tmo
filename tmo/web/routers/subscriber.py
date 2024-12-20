# mypy: disable-error-code="return-value"

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import contains_eager
from sqlmodel import col, select

from ...db.models.tables import Detail, Subscriber
from ...lib.utilities import cast_as_qa
from ..dependencies import SessionDependency
from .responses import ReadSubscriber, ReadSubscriberDetails

router = APIRouter(prefix="/subscriber")


@router.get("")
async def get_subscribers(
    *, start: int = 0, count: int = Query(default=100, le=100), session: SessionDependency
) -> list[ReadSubscriber]:
    return session.exec(select(Subscriber).order_by(col(Subscriber.id).asc()).offset(start).limit(count)).all()


@router.get("/{id}")
async def get_subscriber(*, id: int, session: SessionDependency) -> ReadSubscriberDetails:
    subscriber = (
        session.exec(
            select(Subscriber)
            .join(Detail)
            .options(contains_eager(cast_as_qa(Subscriber.details)))
            .order_by(col(Detail.bill_id).asc())
            .where(Subscriber.id == id)
        )
        .unique()
        .first()
    )

    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber could not be found")

    return subscriber
