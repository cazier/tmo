import decimal
import typing

import pydantic

from ....db.models.tables import BillScalar, DetailScalar, SubscriberScalar


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
