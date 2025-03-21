import datetime
import decimal
import typing

from pydantic import PlainSerializer
from sqlmodel import Field, Relationship, SQLModel

JsonDecimal = typing.Annotated[decimal.Decimal, PlainSerializer(float, return_type=float, when_used="json")]


def decimal_field(
    default: decimal.Decimal = decimal.Decimal("0"),
    max_digits: int = 8,
    decimal_places: int = 2,
    **kwargs: typing.Any,
) -> typing.Any:
    return Field(default=default, max_digits=max_digits, decimal_places=decimal_places, **kwargs)


class BaseModel(SQLModel):
    id: int = Field(default=None, primary_key=True)


## Many-to-Many Relationship Links
class BillSubscriberLink(SQLModel, table=True):
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)


## Base Models (containing actual scalar values)
class SubscriberScalar(SQLModel):
    name: str
    number: str = Field(unique=True, max_length=20)
    format: str = Field(default="us", max_length=2)


class BillScalar(SQLModel):
    date: datetime.date = Field(unique=True)
    total: JsonDecimal = decimal_field()

    def update_total(self) -> None:
        self.total = sum([item.total for item in self.details + self.charges], start=decimal.Decimal("0"))  # type: ignore[attr-defined]


class DetailScalar(SQLModel):
    phone: typing.Annotated[JsonDecimal, "$"] = decimal_field()
    line: typing.Annotated[JsonDecimal, "$"] = decimal_field()
    insurance: typing.Annotated[JsonDecimal, "$"] = decimal_field()
    usage: typing.Annotated[JsonDecimal, "$"] = decimal_field()

    total: JsonDecimal = decimal_field()

    minutes: typing.Annotated[int, "#"] = Field(default=0)
    messages: typing.Annotated[int, "#"] = Field(default=0)
    data: typing.Annotated[JsonDecimal, "#"] = decimal_field(decimal_places=4)


class ChargeScalar(SQLModel):
    name: str
    split: bool = Field(default=False)
    total: typing.Annotated[JsonDecimal, "$"] = decimal_field()


## Relationship Definitions
class Subscriber(SubscriberScalar, BaseModel, table=True):
    details: list["Detail"] = Relationship(back_populates="subscriber")
    bills: list["Bill"] = Relationship(back_populates="subscribers", link_model=BillSubscriberLink)


class Bill(BillScalar, BaseModel, table=True):
    charges: list["Charge"] = Relationship(back_populates="bill")
    details: list["Detail"] = Relationship(back_populates="bill")
    subscribers: list[Subscriber] = Relationship(back_populates="bills", link_model=BillSubscriberLink)


class Detail(DetailScalar, BaseModel, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="details")

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: Subscriber = Relationship(back_populates="details")


class Charge(ChargeScalar, BaseModel, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="charges")
