# mypy: disable-error-code="return-value"
import fastapi
from sqlmodel import select

from ...db.models import Bill, Charge, Detail, Subscriber
from ..dependencies import SessionDependency
from .bill import router as bill
from .charge import router as charge
from .detail import router as detail
from .models.get import ReadBill
from .models.post import PostFilledBill
from .subscriber import router as subscriber

api = fastapi.APIRouter(prefix="/api", include_in_schema=True)

api.include_router(bill)
api.include_router(charge)
api.include_router(detail)
api.include_router(subscriber)


@api.post("/fill")
async def post_filled_bill(*, data: PostFilledBill, session: SessionDependency) -> ReadBill:
    with session.begin_nested() as transaction:
        with session.begin_nested() as bill_transaction:
            _bill = Bill(date=data.date, total=data.total)

            session.add(_bill)
            bill_transaction.commit()

        with session.begin_nested() as charge_transaction:
            for _charge in data.charges:
                session.add(Charge(name=_charge.name, split=_charge.split, total=_charge.total, bill_id=_bill.id))

            charge_transaction.commit()

        with session.begin_nested() as subscriber_transaction:
            for subscriber in data.subscribers:
                _subscriber = session.exec(select(Subscriber).where(Subscriber.number == subscriber.number)).one()
                _detail = Detail(**subscriber.model_dump(), bill_id=_bill.id, subscriber_id=_subscriber.id)

                _subscriber.details.append(_detail)
                _subscriber.bills.append(_bill)
                session.add(_subscriber)
            subscriber_transaction.commit()

        transaction.commit()

    return _bill
