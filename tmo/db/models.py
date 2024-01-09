import dataclasses
import datetime
import decimal
import itertools
import typing

from pydantic import Field as Pield
from pydantic import PlainSerializer, computed_field, field_validator, model_validator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
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


class _CanStepThroughFields(SQLModel):
    @typing.overload
    def _fields_by_annotation(self, string: str) -> str:
        ...

    @typing.overload
    def _fields_by_annotation(self, klass: type[_T]) -> _T:
        ...

    def _fields_by_annotation(self, string: str = "", klass: typing.Optional[type[_T]] = None) -> tuple[str, str | _T]:
        for name, field in itertools.chain(self.model_fields.items(), self.model_computed_fields.items()):
            for item in getattr(field, "metadata", getattr(getattr(field, "return_type", None), "__metadata__", [])):
                if klass and isinstance(item, klass):
                    yield name, item
                elif isinstance(item, str) and item == string:
                    yield name, item


class _Base_Model(SQLModel):
    id: typing.Optional[int] = Field(default=None, primary_key=True)


class _SubscriberBase(SQLModel):
    number: str = Field(unique=True, max_length=20)
    name: typing.Annotated[str, Render("header", 1, formatter=lambda k: k.split(" ")[0])]


def total(self) -> JsonDecimal:
    breakpoint()
    nums = [(name, getattr(self, name)) for name, _ in self._fields_by_annotation(string="$")]
    breakpoint()
    return sum([i[1] for i in nums])


class Subscriber(_SubscriberBase, _Base_Model, table=True):
    number_format: str = Field(default="us", max_length=2)

    details: list["Detail"] = Relationship(back_populates="subscriber")
    bills: list["Bill"] = Relationship(back_populates="subscribers", link_model=_Subscriber_Bill_Link)

    # TODO: This should probably be a column property
    count: typing.ClassVar[int] = hybrid_property(lambda k: len(k.details))


class _BillBase(SQLModel):
    date: datetime.date = Field(unique=True)

    # total: typing.ClassVar[decimal.Decimal] = hybrid_property(lambda k: sum(i.total for i in k.details + k.charges))
    # @computed_field
    # @property
    # def total(self) -> JsonDecimal:
    #     return JsonDecimal(sum([column.total for column in self.charges] + [column.details.total for column in self.subscribers]))


class Bill(_BillBase, _Base_Model, table=True):
    charges: list["Charge"] = Relationship(back_populates="bill")
    details: list["Detail"] = Relationship(back_populates="bill")
    subscribers: list["Subscriber"] = Relationship(back_populates="bills", link_model=_Subscriber_Bill_Link)


class BillRead(_BillBase):
    id: int


class _DetailBase(_CanStepThroughFields, SQLModel):
    _decimals = {"default": 0, "max_digits": 8, "decimal_places": 2}

    phone: typing.Annotated[JsonDecimal, Render("changes", 1, name="Phone Cost"), "$"] = Field(**_decimals)
    line: typing.Annotated[JsonDecimal, Render("charges", 2, name="Line Cost"), "$"] = Field(**_decimals)
    insurance: typing.Annotated[JsonDecimal, Render("charges", 3, name="Insurance"), "$"] = Field(**_decimals)
    usage: typing.Annotated[JsonDecimal, Render("charges", 4, name="Usage Charges"), "$"] = Field(**_decimals)

    @computed_field
    @property
    def total(self) -> typing.Annotated[JsonDecimal, Render("summary", 1, name="Total Charges")]:
        # return JsonDecimal(sum([self.phone, self.line, self.insurance, self.usage]))
        return JsonDecimal(sum(getattr(self, name) for name, _ in self._fields_by_annotation("$")))

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
    details: _DetailBase
    total: JsonDecimal = None

    @model_validator(mode="after")
    def _assign_total(self) -> typing.Self:
        self.total = self.details.total
        return self


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
