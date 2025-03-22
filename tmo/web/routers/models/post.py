import decimal
import typing

import pydantic

from ....db.models.tables import BillScalar, ChargeScalar, DetailScalar, SubscriberScalar


class PostBill(BillScalar):
    pass


class PostSubscriber(SubscriberScalar):
    pass


class PostDetail(DetailScalar):
    @pydantic.model_validator(mode="after")
    def calculate_total(self) -> typing.Self:
        total = decimal.Decimal()

        for name, info in self.model_fields.items():
            if name != "total" and "$" in info.metadata:
                total += getattr(self, name)

        self.total = total
        return self


class PostCharge(ChargeScalar):
    pass


class FillSubscriber(PostSubscriber, PostDetail):
    pass


class PostFilledBill(PostBill):
    subscribers: list[FillSubscriber] = pydantic.Field(default_factory=list)
    charges: list[PostCharge] = pydantic.Field(default_factory=list)
