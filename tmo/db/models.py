import dataclasses
import datetime
import decimal
import typing

from pydantic import PlainSerializer, computed_field
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, SQLModel

_T = typing.TypeVar("_T")


@dataclasses.dataclass(order=True)
class Render:
    @staticmethod
    def noop(value: _T) -> _T:
        return value

    section: str
    order: int
    name: str = dataclasses.field(default="", compare=False)
    formatter: typing.Callable[[_T], _T] = dataclasses.field(default=noop, compare=False)

    def with_name(self, fallback: str) -> "Render":
        if self.name == "":
            self.name = fallback

        return self


JsonDecimal = typing.Annotated[decimal.Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class _Subscriber_Bill_Link(SQLModel, table=True):
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)


class _Base_Model(SQLModel):
    id: typing.Optional[int] = Field(default=None, primary_key=True)


class _SubscriberBase(SQLModel):
    number: str = Field(unique=True, max_length=20)
    name: typing.Annotated[str, Render("header", 1, formatter=lambda k: k.split(" ")[0])]


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
    _decimals = {"default": 0, "max_digits": 8, "decimal_places": 2}

    phone: typing.Annotated[JsonDecimal, Render("changes", 1, name="Phone Cost")] = Field(**_decimals)
    line: typing.Annotated[JsonDecimal, Render("charges", 2, name="Line Cost")] = Field(**_decimals)
    insurance: typing.Annotated[JsonDecimal, Render("charges", 3, name="Insurance")] = Field(**_decimals)
    usage: typing.Annotated[JsonDecimal, Render("charges", 4, name="Usage Charges")] = Field(**_decimals)

    @computed_field
    @property
    def total(self) -> typing.Annotated[float, Render("summary", 1, name="Total Charges")]:
        return float(sum([self.phone, self.line, self.insurance, self.usage]))

    minutes: typing.Annotated[int, Render("usage", 1, name="Minutes (min)")] = Field(default=0)
    messages: typing.Annotated[int, Render("usage", 2, name="Messages (#)")] = Field(default=0)
    data: typing.Annotated[JsonDecimal, Render("usage", 3, name="Data (GB)")] = Field(**_decimals)


class Detail(_DetailBase, _Base_Model, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="details")

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: Subscriber = Relationship(back_populates="details")


class _ChargeBase(SQLModel):
    name: str

    total: JsonDecimal = Field(default=0, max_digits=4, decimal_places=2)


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
    detail: _DetailBase


class MonthValidator(SQLModel):
    class MVSubscriber(_SubscriberBase, _DetailBase, SQLModel):
        pass

    sections: typing.ClassVar[tuple[str, ...]] = ("header", "charges", "usage", "summary")

    id: int
    date: datetime.date

    charges: list[ChargeRead] = []

    subscribers: list[MVSubscriber]
    previous: list[MVSubscriber] = []

    @computed_field
    @property
    def total(self) -> float:
        return sum(field.total for field in self.subscribers + self.charges)

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
