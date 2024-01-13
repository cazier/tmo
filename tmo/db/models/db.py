import datetime
import typing

from sqlmodel import Field, Relationship, SQLModel

from .utilities import AnnotatedSQLModel, JsonDecimal, Render, decimal_field


class BaseModel(SQLModel):
    id: typing.Optional[int] = Field(default=None, primary_key=True)


## Many-to-Many Relationship Links
class BillSubscriberLink(SQLModel, table=True):
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)


## Base Models (containing actual scalar values)
class SubscriberScalar(AnnotatedSQLModel):
    number: str = Field(unique=True, max_length=20)
    name: typing.Annotated[str, Render("header", 1, formatter=lambda k: k.split(" ")[0])]


class BillScalar(SQLModel):
    date: datetime.date = Field(unique=True)
    total: JsonDecimal = Field(default=0, max_digits=8, decimal_places=2)


class DetailScalar(AnnotatedSQLModel):
    phone: typing.Annotated[JsonDecimal, Render("charges", 1, name="Phone Cost"), "$"] = decimal_field()
    line: typing.Annotated[JsonDecimal, Render("charges", 2, name="Line Cost"), "$"] = decimal_field()
    insurance: typing.Annotated[JsonDecimal, Render("charges", 3, name="Insurance"), "$"] = decimal_field()
    usage: typing.Annotated[JsonDecimal, Render("charges", 4, name="Usage Charges"), "$"] = decimal_field()

    total: typing.Annotated[JsonDecimal, Render("summary", 1, name="Total Charges")] = decimal_field()

    minutes: typing.Annotated[int, Render("usage", 1, name="Minutes (min)")] = Field(default=0)
    messages: typing.Annotated[int, Render("usage", 2, name="Messages (#)")] = Field(default=0)
    data: typing.Annotated[JsonDecimal, Render("usage", 3, name="Data (GB)")] = decimal_field()


class ChargeScalar(AnnotatedSQLModel):
    name: str

    total: typing.Annotated[JsonDecimal, "$"] = decimal_field()


## Relationship Definitions
class Subscriber(SubscriberScalar, BaseModel, table=True):
    number_format: str = Field(default="us", max_length=2)

    details: list["Detail"] = Relationship(back_populates="subscriber")
    bills: list["Bill"] = Relationship(back_populates="subscribers", link_model=BillSubscriberLink)

    count: int = Field(default=0)


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
