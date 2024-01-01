import datetime
import decimal
import functools
import itertools
import typing

from pydantic import PlainSerializer, computed_field
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, SQLModel

_M = typing.TypeVar("_M", bound=SQLModel)
_K = typing.TypedDict(
    "_K", {"section": str, "name": str, "order": int, "formatter": typing.Callable[[typing.Any], typing.Any]}
)


def _renders(
    section: str,
    order: int,
    name: str = "",
    computed: bool = False,
    formatter: typing.Optional[typing.Callable[[typing.Any], typing.Any]] = None,
    **kwargs: typing.Any,
) -> dict[str, dict[str, dict[str, typing.Any]]]:
    if name != "":
        kwargs.update(name=name)

    if formatter is None:
        _F = typing.TypeVar("_F")

        def formatter(value: _F) -> _F:
            return value

    kwargs.update(section=section, order=order, formatter=formatter)

    kwargs = {"json_schema_extra": kwargs}

    if computed:
        return kwargs

    return {"schema_extra": kwargs}


JsonDecimal = typing.Annotated[decimal.Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class _Subscriber_Bill_Link(SQLModel, table=True):
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)


class _Base_Model(SQLModel):
    id: typing.Optional[int] = Field(default=None, primary_key=True)


class _SubscriberBase(SQLModel):
    number: str = Field(unique=True, max_length=20)
    name: str = Field(**_renders(section="header", order=1, formatter=lambda k: k.split(" ")[0]))


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

    phone: JsonDecimal = Field(**_decimals, **_renders("charges", order=1, name="Phone Cost"))
    line: JsonDecimal = Field(**_decimals, **_renders("charges", order=2, name="Line Cost"))
    insurance: JsonDecimal = Field(**_decimals, **_renders("charges", order=3, name="Insurance"))
    usage: JsonDecimal = Field(**_decimals, **_renders("charges", order=4, name="Usage Charges"))

    @computed_field(**_renders("summary", order=1, name="Total Charges", computed=True))
    @property
    def total(self) -> float:
        return float(sum([self.phone, self.line, self.insurance, self.usage]))

    minutes: int = Field(default=0, **_renders("usage", order=1, name="Minutes (min)"))
    messages: int = Field(default=0, **_renders("usage", order=2, name="Messages (#)"))
    data: JsonDecimal = Field(**_decimals, **_renders("usage", order=3, name="Data (GB)"))


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
    detail: Detail


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


@functools.lru_cache(typed=True)
def keys(*models: _M) -> dict[str, _K]:
    if not models:
        models = (_DetailBase, _SubscriberBase)

    return {
        key: {
            "section": field["section"],
            "formatter": field["formatter"],
            "name": field.get("name", key),
        }
        for model in map(lambda m: m.model_construct(), models)
        for key, field in sorted(
            (
                (name, _field.json_schema_extra)
                for name, _field in itertools.chain(
                    model.model_fields.items(),
                    model.model_computed_fields.items(),
                )
                if _field.json_schema_extra is not None
            ),
            key=lambda k: (
                k[1]["section"],
                k[1]["order"],
            ),
        )
    }
