# mypy: disable-error-code="return-value"
import typing

import fastapi
import pydantic
from sqlalchemy.orm import contains_eager
from sqlmodel import col, select

from ...db.models.tables import Detail, Subscriber
from ...lib.utilities import cast_as_qa
from ..dependencies import SessionDependency
from ..exceptions import APIException
from .models.get import ReadSubscriber, ReadSubscriberDetails
from .models.post import PostSubscriber

router = fastapi.APIRouter()


@router.get("/subscriber")
async def get_subscribers(
    *,
    start: typing.Annotated[int, fastapi.Query(ge=0)] = 0,
    count: typing.Annotated[int, fastapi.Query(gt=1, le=100)] = 10,
    session: SessionDependency,
) -> list[ReadSubscriber]:
    return session.exec(select(Subscriber).order_by(col(Subscriber.id).asc()).offset(start).limit(count)).all()


class Lookup(pydantic.BaseModel):
    name: str = ""
    number: str = ""

    @pydantic.model_validator(mode="after")
    def _ensure_exactly_one(self) -> typing.Self:
        assert (self.name or self.number) and not (self.name and self.number)
        return self


@router.get("/subscriber/lookup")
async def get_subscriber_lookup(*, name: str = "", number: str = "", session: SessionDependency) -> ReadSubscriber:
    if name and number or (not name and not number):
        raise APIException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Exactly one of name or number must be provided"
        )

    if name:
        sql_query = Subscriber.name == name

    if number:
        sql_query = Subscriber.number == number

    subscriber = session.exec(select(Subscriber).where(sql_query)).one_or_none()

    if not subscriber:
        raise APIException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Subscriber could not be found")

    return subscriber


@router.get("/subscriber/{id}")
async def get_subscriber(
    *,
    id: typing.Annotated[int, fastapi.Path(ge=0)],
    session: SessionDependency,
) -> ReadSubscriberDetails:
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
        raise APIException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Subscriber could not be found")

    return subscriber


@router.post("/subscriber")
async def post_subscriber(*, data: PostSubscriber, session: SessionDependency) -> ReadSubscriber:
    subscriber = session.exec(select(Subscriber).where(Subscriber.number == data.number)).first()

    if subscriber is not None:
        raise APIException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail=f"A subscriber with the number {data.number} already exists (ID={subscriber.id})",
        )

    subscriber = Subscriber(name=data.name, number=data.number, format=data.format)

    session.add(subscriber)
    session.commit()
    session.refresh(subscriber)

    return subscriber
