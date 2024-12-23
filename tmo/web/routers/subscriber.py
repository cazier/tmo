# mypy: disable-error-code="return-value"
import typing

import fastapi
from sqlalchemy.orm import contains_eager
from sqlmodel import col, select

from ...db.models.tables import Detail, Subscriber
from ...lib.utilities import cast_as_qa
from ..dependencies import SessionDependency
from ..exceptions import APIException
from .responses import ReadSubscriber, ReadSubscriberDetails

router = fastapi.APIRouter(prefix="/subscriber")


@router.get("")
async def get_subscribers(
    *,
    start: typing.Annotated[int, fastapi.Query(ge=0)] = 0,
    count: typing.Annotated[int, fastapi.Query(gt=1, le=100)] = 10,
    session: SessionDependency,
) -> list[ReadSubscriber]:
    return session.exec(select(Subscriber).order_by(col(Subscriber.id).asc()).offset(start).limit(count)).all()


@router.get("/{id}")
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
        raise APIException(status_code=404, detail="Subscriber could not be found")

    return subscriber
