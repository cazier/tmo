import datetime
import decimal

import pydantic


class Subscriber(pydantic.BaseModel):
    name: str
    number: str

    minutes: int
    messages: int
    data: decimal.Decimal

    phone: decimal.Decimal
    line: decimal.Decimal
    insurance: decimal.Decimal
    usage: decimal.Decimal


class Charge(pydantic.BaseModel):
    name: str
    split: bool = False
    total: decimal.Decimal


class _Bill(pydantic.BaseModel):
    date: datetime.date
    total: decimal.Decimal = pydantic.Field(default_factory=decimal.Decimal)


class Bill(pydantic.BaseModel):
    date: datetime.date
    total: decimal.Decimal = pydantic.Field(default_factory=decimal.Decimal)
    subscribers: list[Subscriber] = pydantic.Field(default_factory=list)
    charges: list[Charge] = pydantic.Field(default_factory=list)
