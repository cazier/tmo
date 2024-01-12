import datetime
import typing

from pydantic import model_validator
from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel

from tmo.db.utilities import AnnotatedSQLModel, BaseModel, JsonDecimal, Render


class _Subscriber_Bill_Link(SQLModel, table=True):
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)


class _SubscriberBase(SQLModel):
    number: str = Field(unique=True, max_length=20)
    name: typing.Annotated[str, Render("header", 1, formatter=lambda k: k.split(" ")[0])]


class Subscriber(_SubscriberBase, BaseModel, table=True):
    number_format: str = Field(default="us", max_length=2)

    details: list["Detail"] = Relationship(back_populates="subscriber")
    bills: list["Bill"] = Relationship(back_populates="subscribers", link_model=_Subscriber_Bill_Link)

    count: int = 0


@event.listens_for(Subscriber.bills, "append")
def _update_bill_total(target: Subscriber, *_) -> None:
    target.count = 1 + len(target.bills)


class _BillBase(SQLModel):
    date: datetime.date = Field(unique=True)
    total: JsonDecimal = Field(default=0, max_digits=8, decimal_places=2)


class Bill(_BillBase, BaseModel, table=True):
    charges: list["Charge"] = Relationship(back_populates="bill")
    details: list["Detail"] = Relationship(back_populates="bill")
    subscribers: list["Subscriber"] = Relationship(back_populates="bills", link_model=_Subscriber_Bill_Link)


@event.listens_for(Bill.charges, "append")
@event.listens_for(Bill.details, "append")
def _update_bill_total(target: Bill, value: "Detail", *_) -> None:
    target.total = value.total + sum(item.total for item in target.details + target.charges)


class BillRead(_BillBase):
    id: int


class _DetailBase(AnnotatedSQLModel):
    _decimals = {"default": 0, "max_digits": 8, "decimal_places": 2}

    phone: typing.Annotated[JsonDecimal, Render("changes", 1, name="Phone Cost"), "$"] = Field(**_decimals)
    line: typing.Annotated[JsonDecimal, Render("charges", 2, name="Line Cost"), "$"] = Field(**_decimals)
    insurance: typing.Annotated[JsonDecimal, Render("charges", 3, name="Insurance"), "$"] = Field(**_decimals)
    usage: typing.Annotated[JsonDecimal, Render("charges", 4, name="Usage Charges"), "$"] = Field(**_decimals)

    total: typing.Annotated[JsonDecimal, Render("charges", 5, name="Total Charges")] = Field(**_decimals)

    minutes: typing.Annotated[int, Render("usage", 1, name="Minutes (min)")] = Field(default=0)
    messages: typing.Annotated[int, Render("usage", 2, name="Messages (#)")] = Field(default=0)
    data: typing.Annotated[JsonDecimal, Render("usage", 3, name="Data (GB)")] = Field(**_decimals)


class Detail(_DetailBase, BaseModel, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="details")

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: Subscriber = Relationship(back_populates="details")


@event.listens_for(Detail, "init")
def _init_detail(target: Detail, _: tuple[typing.Any], kwargs: dict[str, typing.Any]):
    kwargs.setdefault("total", sum(kwargs[name] for name, _ in target.fields_by_annotation(string="$")))


# @event.listens_for(Detail.phone, "set")
# @event.listens_for(Detail.line, "set")
# @event.listens_for(Detail.insurance, "set")
# @event.listens_for(Detail.usage, "set")
# def _update_detail(target: Detail, value: JsonDecimal, oldvalue: JsonDecimal, *_):
#     if oldvalue != orm.LoaderCallableStatus.NO_VALUE:
#         value = value - oldvalue
#         target.bill.total += value

#     target.total = value + sum(getattr(target, name) or 0 for name, _ in target._fields_by_annotation(string="$"))


class _ChargeBase(AnnotatedSQLModel):
    name: str

    total: typing.Annotated[JsonDecimal, "$"] = Field(default=0, max_digits=4, decimal_places=2)


class Charge(_ChargeBase, BaseModel, table=True):
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
    details: _DetailBase


class BillRender(_BillBase):
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
