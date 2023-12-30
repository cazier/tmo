import datetime
import decimal
import functools
import typing

from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, SQLModel


def with_pretty(name: str) -> dict[str, dict[str, dict[str, str]]]:
    return {"schema_extra": {"json_schema_extra": {"pretty": name}}}


class _Subscriber_Bill_Link(SQLModel, table=True):
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)


class _Base_Model(SQLModel):
    id: typing.Optional[int] = Field(default=None, primary_key=True)


class _SubscriberBase(SQLModel):
    name: str
    number: str = Field(unique=True, max_length=20)


class Subscriber(_SubscriberBase, _Base_Model, table=True):
    number_format: str = Field(default="us", max_length=2)

    details: list["Detail"] = Relationship(back_populates="subscriber")
    bills: list["Bill"] = Relationship(back_populates="subscribers", link_model=_Subscriber_Bill_Link)

    count: typing.ClassVar[int] = hybrid_property(lambda k: len(k.details))


class _BillBase(SQLModel):
    date: datetime.date = Field(unique=True)

    total: typing.ClassVar[decimal.Decimal] = hybrid_property(lambda k: sum(i.total for i in k.details + k.charges))


class Bill(_BillBase, _Base_Model, table=True):
    charges: list["Charge"] = Relationship(back_populates="bill")
    details: list["Detail"] = Relationship(back_populates="bill")
    subscribers: list["Subscriber"] = Relationship(back_populates="bills", link_model=_Subscriber_Bill_Link)


class BillRead(_BillBase):
    id: int


class _DetailBase(SQLModel):
    line: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2, **with_pretty("Line Cost"))
    phone: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2, **with_pretty("Phone Cost"))
    usage: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2, **with_pretty("Usage Charges"))
    insurance: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2, **with_pretty("Insurance"))

    total: typing.ClassVar[decimal.Decimal] = hybrid_property(lambda k: sum([k.phone, k.line, k.insurance, k.usage]))

    minutes: int = Field(default=0, **with_pretty("Minutes (min)"))
    messages: int = Field(default=0, **with_pretty("Messages (#)"))
    data: decimal.Decimal = Field(default=0, max_digits=5, decimal_places=2, **with_pretty("Data (GB)"))


class Detail(_DetailBase, _Base_Model, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="details")

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: Subscriber = Relationship(back_populates="details")


class _ChargeBase(SQLModel):
    name: str

    total: decimal.Decimal = Field(default=0, max_digits=4, decimal_places=2)


class Charge(_ChargeBase, _Base_Model, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="charges")


class ChargeRead(_ChargeBase):
    pass


class SubscribersRead(_SubscriberBase):
    id: int


class SubscriberRead(SubscribersRead):
    count: int

    bills: list["BillRead"]


class BillReadWithSubscribers(BillRead):
    subscribers: list[SubscribersRead]


class SubscriberReadWithDetails(SubscribersRead):
    detail: Detail


class MonthValidator(SQLModel):
    class MVSubscriber(_SubscriberBase, _DetailBase, SQLModel):
        pass

    id: int
    date: datetime.date

    charges: list[ChargeRead] = []
    subscribers: list[MVSubscriber]

    @staticmethod
    def stuff_data(data: list[tuple[Bill, Subscriber, Detail]]) -> dict[str, typing.Any]:
        [(bill, *_), *_] = data
        return {
            "id": bill.id,
            "date": bill.date,
            "charges": bill.charges,
            "subscribers": [
                {
                    **subscriber.model_dump(mode="json"),
                    **detail.model_dump(mode="json"),
                }
                for (_, subscriber, detail) in data
            ],
        }


_M = typing.TypeVar("_M", bound=SQLModel)


@functools.cache
def keys(*models: _M) -> dict[str, str]:
    if not models:
        models = (Detail, Subscriber)

    return {
        key: (value.json_schema_extra or {}).get("pretty", key)
        for model in models
        for key, value in model.model_fields.items()
    }
