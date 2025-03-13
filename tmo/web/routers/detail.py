# mypy: disable-error-code="return-value"
import typing

import fastapi

from ...db.models import Bill, Detail, Subscriber
from ..dependencies import SessionDependency
from ..exceptions import APIException
from .models.get import ReadDetail
from .models.post import PostDetail

router = fastapi.APIRouter()


@router.post("/detail")
async def post_detail(
    *,
    data: PostDetail,
    bill_id: typing.Annotated[int, fastapi.Query(alias="bill")],
    subscriber_id: typing.Annotated[int, fastapi.Query(alias="subscriber")],
    session: SessionDependency,
) -> ReadDetail:
    bill = session.get(Bill, bill_id)

    if bill is None:
        raise APIException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Bill could not be found")

    subscriber = session.get(Subscriber, subscriber_id)

    if subscriber is None:
        raise APIException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Subscriber could not be found")

    detail = Detail.model_validate(data, update={"bill_id": bill_id, "subscriber_id": subscriber_id})

    session.add(detail)
    session.commit()
    session.refresh(detail)

    return detail
