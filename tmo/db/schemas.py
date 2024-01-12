import typing

from pydantic import model_validator

from tmo.db.models.models import Bill, BillScalar, ChargeScalar, DetailScalar, SubscriberScalar


class BillRead(BillScalar):
    id: int


class ChargeRead(ChargeScalar):
    pass


class SubscribersRead(SubscriberScalar):
    id: int


class SubscriberRead(SubscribersRead):
    count: int

    bills: list[BillRead]


class BillReadWithSubscribers(BillRead):
    subscribers: list[SubscribersRead]


class SubscriberReadWithDetails(SubscribersRead):
    details: DetailScalar


class BillRender(BillScalar):
    id: int
    charges: list[ChargeRead]
    subscribers: list[SubscriberReadWithDetails]

    sections: typing.ClassVar[tuple[str, ...]] = ("header", "charges", "usage", "summary")

    @model_validator(mode="before")
    @classmethod
    def _test(cls, data: Bill):
        bill = {
            **data.model_dump(),
            "charges": data.charges,
            "subscribers": [
                {
                    **subscriber.model_dump(),
                    "details": [{**detail.model_dump()} for detail in subscriber.details if detail.bill_id == data.id][
                        0
                    ],
                }
                for subscriber in data.subscribers
            ],
        }

        return bill
