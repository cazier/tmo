import collections
import datetime
import decimal
import typing

import arrow
from pydantic import BaseModel, Field, dataclasses, field_validator, model_validator

from ...config import config
from ..routers.models.get import BillRender, SubscriberReadWithDetails

Unset = object()
Skip = object()


@dataclasses.dataclass
class Element:
    title: str
    section: str
    id: str | object = Unset
    field: str | object = Unset
    is_currency: bool = False


class Totals(BaseModel):
    total: decimal.Decimal
    recap: decimal.Decimal
    klass: str = ""

    @model_validator(mode="after")
    def _assign_klass(self) -> typing.Self:
        if self.total < self.recap:
            self.klass = "is-currency-less"
        if self.total > self.recap:
            self.klass = "is-currency-more"
        return self


class Charts(BaseModel):
    names: list[str]
    colors: list[str]

    data: list[decimal.Decimal]
    minutes: list[int]
    messages: list[int]


_list = Field(default_factory=list)  # type: ignore


class _Shared(BaseModel):
    name: str
    present: decimal.Decimal
    previous: decimal.Decimal


class BillsRender(BaseModel):
    month: datetime.date

    current: typing.Annotated[BillRender, Field(exclude=True, repr=False)]
    previous: typing.Annotated[BillRender, Field(exclude=True, repr=False)]

    phone: typing.Annotated[list[decimal.Decimal], _list, Element("Phone Cost", "charges", is_currency=True)]
    line: typing.Annotated[list[decimal.Decimal], _list, Element("Line Cost", "charges", is_currency=True)]
    insurance: typing.Annotated[list[decimal.Decimal], _list, Element("Insurance", "charges", is_currency=True)]
    usage: typing.Annotated[list[decimal.Decimal], _list, Element("Usage Charges", "charges", is_currency=True)]

    minutes: typing.Annotated[list[int], _list, Element("Minutes (min)", "usage")]
    messages: typing.Annotated[list[int], _list, Element("Messages (#)", "usage")]
    data: typing.Annotated[list[decimal.Decimal], _list, Element("Data (GB)", "usage")]

    totals: typing.Annotated[list[decimal.Decimal], _list, Element("Total Charges", "summary", field="total")]
    recap: typing.Annotated[list[decimal.Decimal], _list, Element("(Last Month)", "recap", field=Skip)]

    @field_validator("month", mode="after")
    @classmethod
    def _month(cls, v: datetime.date) -> datetime.date:
        return v.replace(day=1)

    @property
    def total(self) -> decimal.Decimal:
        return self.current.total

    @property
    def months(self) -> typing.Annotated[tuple[datetime.date, datetime.date | None], Element("date", "Date")]:
        last = arrow.get(self.month).shift(months=-1).replace(day=1).date()
        next = arrow.get(self.month).shift(months=+1).replace(day=1).date()

        if next > datetime.date.today():
            return last, None

        return last, next

    @property
    def names(self) -> typing.Iterator[str]:
        yield from (self._split(subscriber.name) for subscriber in self.current.subscribers)

    @property
    def owed(self) -> dict[str, decimal.Decimal]:
        owed: dict[str, decimal.Decimal] = collections.defaultdict(decimal.Decimal)

        for subscriber in self.current.subscribers:
            if not config.frontend.dependents.get(subscriber.number):
                continue

            for dependent in config.frontend.dependents[subscriber.number]:
                try:
                    owed[self._split(subscriber.name)] += (
                        self._lookup_subscriber(number=dependent).details.total + self.split_charges
                    )

                except LookupError:
                    continue

        return owed

    @property
    def split_charges(self) -> decimal.Decimal:
        return sum((charge.total for charge in self.current.charges if charge.split), start=decimal.Decimal()) / len(
            self.current.subscribers
        )

    @property
    def charges(self) -> list[_Shared]:
        return [
            _Shared(
                name=charge.name,
                present=charge.total,
                previous=next(
                    (prev.total for prev in self.previous.charges if prev.name == charge.name), decimal.Decimal(0)
                ),
            )
            for charge in sorted(self.current.charges, key=lambda k: k.name)
        ]

    def _lookup_subscriber(self, *, name: str = "", number: str = "") -> SubscriberReadWithDetails:
        number = number.replace("-", "")

        if name and number or (name == "" and number == ""):
            raise ValueError("Must supply exactly one of name or number, but not both.")

        for subscriber in self.current.subscribers:
            if number and subscriber.number.replace("-", "") == number:
                return subscriber
            if name and subscriber.name == name:
                return subscriber

        raise LookupError(f"Could not find the user: {name if name else number}")

    @model_validator(mode="before")
    @classmethod
    def _update_elements(cls, data: typing.Any) -> typing.Any:
        for name, field in cls.model_fields.items():
            for metadata in field.metadata:
                if isinstance(metadata, Element):
                    if metadata.id is Unset:
                        metadata.id = name

                    if metadata.field is Unset:
                        metadata.field = name

        return data

    @model_validator(mode="after")
    def _transpose_subscriber_info(self) -> typing.Self:
        for field in self.model_fields:
            try:
                element = self.get_element(field)

            except TypeError:
                continue

            if element.field is Skip:
                continue

            for subscriber in self.current.subscribers:
                getattr(self, field).append(getattr(subscriber.details, element.field))  # type: ignore[call-overload]

        previous = {subscriber.number: subscriber.details.total for subscriber in self.previous.subscribers}

        for current in self.current.subscribers:
            self.recap.append(previous.get(current.number, decimal.Decimal(0)))

        return self

    def get(self, field: str) -> typing.Iterator[int | decimal.Decimal]:
        try:
            self.get_element(field)

        except KeyError:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {field!r}")

        except TypeError:
            raise ValueError(f"Invalid (non-transposed) field '{field}'")

        yield from getattr(self, field)

    def iter_totals(self) -> typing.Iterator[Totals]:
        for total, recap in zip(self.totals, self.recap):
            yield Totals(total=total, recap=recap)

    @classmethod
    def get_element(cls, field: str) -> Element:
        info = cls.model_fields[field]

        for metadata in info.metadata:
            if isinstance(metadata, Element):
                return metadata

        raise TypeError(f"Field '{field}' is not an Element type")

    @classmethod
    def fields_in_section(cls, section: str) -> typing.Iterator[tuple[str, Element]]:
        for field, info in cls.model_fields.items():
            for metadata in info.metadata:
                if isinstance(metadata, Element) and metadata.section == section:
                    yield field, metadata

    @property
    def charts(self) -> Charts:
        colors = [config.frontend.colors[subscriber.number] for subscriber in self.current.subscribers]
        return Charts(
            names=list(self.names), colors=colors, data=self.data, minutes=self.minutes, messages=self.messages
        )

    @staticmethod
    def _split(string: str) -> str:
        return string.split(" ")[0]


def currency_class(value: int | float) -> str:
    if value < 0:
        return "is-currency-negative"

    if value == 0:
        return "is-currency-zero"

    return ""
