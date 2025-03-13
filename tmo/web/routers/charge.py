# mypy: disable-error-code="return-value"
import typing

import fastapi

from ...db.models import Bill, Charge
from ..dependencies import SessionDependency
from ..exceptions import APIException
from .models.get import ReadChargeId
from .models.post import PostCharge

router = fastapi.APIRouter()


@router.post("/charge")
async def post_charge(
    *,
    data: PostCharge,
    bill_id: typing.Annotated[int, fastapi.Query(alias="bill")],
    session: SessionDependency,
) -> ReadChargeId:
    bill = session.get(Bill, bill_id)

    if bill is None:
        raise APIException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Bill could not be found")

    charge = Charge.model_validate(data, update={"bill_id": bill_id})

    session.add(charge)
    session.commit()
    session.refresh(charge)

    return charge
