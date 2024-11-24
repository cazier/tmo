# mypy: disable-error-code="return-value"

import pydantic
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import contains_eager
from sqlmodel import col, select

from ..db.models.tables import Detail, DetailScalar, Subscriber, SubscriberScalar
from ..dependencies import SessionDependency
from ..lib.utilities import cast_as_qa

router = APIRouter(prefix="/subscriber")


class ReadSubscriber(SubscriberScalar):
    id: int


class ReadSubscribersDetail(SubscriberScalar):
    id: int
    detail: DetailScalar = pydantic.Field(alias="details")

    @pydantic.field_validator("detail", mode="before")
    @classmethod
    def get_entry(cls, data: list[DetailScalar]) -> DetailScalar:
        if len(data) != 1:
            raise ValueError("Data must only contain one detail entry")
        return data[0]


class _Details(DetailScalar):
    id: int


class ReadSubscribersDetails(SubscriberScalar):
    id: int
    number_format: str
    details: list[_Details]


@router.get("")
async def get_subscribers(
    *, start: int = 0, count: int = Query(default=100, le=100), session: SessionDependency
) -> list[ReadSubscriber]:
    return session.exec(select(Subscriber).order_by(col(Subscriber.id).asc()).offset(start).limit(count)).all()


@router.get("/{id}")
async def get_subscriber(*, id: int, session: SessionDependency) -> ReadSubscribersDetails:
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
