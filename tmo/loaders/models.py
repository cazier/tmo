import datetime
import decimal

import pydantic


class Subscriber(pydantic.BaseModel):
    name: str
    num: str

    minutes: int
    messages: int
    data: decimal.Decimal

    phone: decimal.Decimal
    line: decimal.Decimal
    insurance: decimal.Decimal
    usage: decimal.Decimal


class Other(pydantic.BaseModel):
    kind: str
    value: decimal.Decimal
    split: bool = False


class Bill(pydantic.BaseModel):
    date: datetime.date
    subscribers: list[Subscriber] = pydantic.Field(default_factory=list)
    other: list[Other] = pydantic.Field(default_factory=list)
