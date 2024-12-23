import decimal
import typing

import pydantic

from ...db.models.tables import BillScalar, ChargeScalar, DetailScalar, JsonDecimal, SubscriberScalar


class _Details(DetailScalar):
    id: int


class ReadBill(BillScalar):
    id: int


class ReadSubscriber(SubscriberScalar):
    id: int


class ReadSubscriberDetail(SubscriberScalar):
    id: int
    detail: DetailScalar = pydantic.Field(alias="details")

    @pydantic.field_validator("detail", mode="before")
    @classmethod
    def get_entry(cls, data: list[DetailScalar]) -> DetailScalar:
        if len(data) != 1:
            raise ValueError("Data must only contain one detail entry")
        return data[0]


class ReadSubscriberDetails(SubscriberScalar):
    id: int
    details: list[_Details]


class ReadSubscriberTotals(ReadSubscriberDetail):
    id: int
    total: JsonDecimal = decimal.Decimal("0")

    @pydantic.model_validator(mode="after")
    def get_total(self) -> typing.Self:
        self.total = self.detail.total
        delattr(self, "detail")
        return self


class ReadCharge(ChargeScalar):
    pass


class ReadDetail(DetailScalar):
    bill_id: int


class ReadBillSubscribersCharges(ReadBill):
    charges: list[ReadCharge]
    subscribers: list[ReadSubscriberDetails]


class ReadBillSubscribersChargesDetail(ReadBill):
    charges: list[ReadCharge]
    subscribers: list[ReadSubscriberDetail]


class ReadBillSubscriberTotalsCharges(ReadBill):
    charges: list[ReadCharge]
    subscribers: list[ReadSubscriberTotals]


class SubscriberReadWithDetails(ReadSubscriber):
    details: DetailScalar


class BillRender(BillScalar):
    id: int
    charges: list[ReadCharge]
    subscribers: list[SubscriberReadWithDetails]
