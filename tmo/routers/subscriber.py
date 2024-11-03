from typing import Sequence

from fastapi import APIRouter, HTTPException, Query
import pydantic
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ..dependencies import SessionDependency
from ..db.models.tables import *



router = APIRouter(prefix="/subscriber")


class ReadSubscriber(SubscriberScalar):
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
    
class _Details(DetailScalar):
    id: int

class ReadSubscribersDetails(SubscriberScalar):
    id: int
    details: list[_Details]

@router.get("")
async def get_subscribers(
    *, start: int = 0, count: int = Query(default=100, le=100), session: SessionDependency
) -> Sequence[ReadSubscriber]:
    return session.exec(select(Subscriber).order_by(Subscriber.id).offset(start).limit(count)).all()


@router.get("/{id}")
async def get_subscriber(*, id: int, session: SessionDependency) -> ReadSubscribersDetails:
    subscriber = (
        session.exec(
            select(Subscriber)
            .options(joinedload(Subscriber.details))
            .join(Subscriber.details)
            .order_by(Detail.bill_id)
            .where(Subscriber.id == id)
        )
        .unique()
        .first()
    )

    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber could not be found")
    return subscriber
