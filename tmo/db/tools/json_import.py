import datetime
import decimal
import json
import pathlib
import typing

import pydantic
from sqlmodel import Session

from tmo import config
from tmo.db.engines import start_engine
from tmo.db.models import Bill, Charge, Detail, Subscriber


class _SubscriberImport(pydantic.BaseModel):
    name: str
    num: str

    minutes: int
    messages: int
    data: decimal.Decimal

    phone: decimal.Decimal
    line: decimal.Decimal
    insurance: decimal.Decimal
    usage: decimal.Decimal


class _Other(pydantic.BaseModel):
    kind: str
    value: decimal.Decimal


class _Bill(pydantic.BaseModel):
    date: datetime.date
    subscribers: list[_SubscriberImport]
    other: list[_Other] = pydantic.Field(default_factory=list)


_bill_cache: dict[datetime.date, Bill] = {}
_user_cache: dict[str, Subscriber] = {}


class _NameMap:  # pylint: disable=too-few-public-methods
    def __init__(self, names: dict[str, str]) -> None:
        self._names = names

    def __getitem__(self, key: str) -> str:
        return self._names.get(key, self._names["default"])


def _load(path: pathlib.Path) -> dict[str, dict[str, typing.Any]]:
    return typing.cast(dict[str, dict[str, typing.Any]], json.loads(path.read_text(encoding="utf-8")))


def _fill(session: Session, bill: _Bill) -> None:
    _name_map = _NameMap(config.load.names)
    _bill = _bill_cache.setdefault(bill.date, Bill(date=bill.date))

    for other in bill.other:
        charge = Charge(name=other.kind, total=other.value, bill=_bill)
        session.add(charge)

    for _data in bill.subscribers:
        surname = _name_map[_data.name]
        name = _data.name + " " + surname
        user = _user_cache.setdefault(_data.num, Subscriber(name=name, number=_data.num))
        user.bills.append(_bill)

        detail = Detail(
            bill=_bill,
            subscriber=user,
            phone=_data.phone,
            line=_data.line,
            insurance=_data.insurance,
            usage=_data.usage,
            minutes=_data.minutes,
            messages=_data.messages,
            data=_data.data,
            total=sum([_data.line, _data.insurance, _data.usage, _data.phone]),
        )
        session.add(detail)

    _bill.total = sum((item.total for item in _bill.details + _bill.charges), start=decimal.Decimal("0"))

    session.add(_bill)
    session.add(user)


def run(path: pathlib.Path) -> None:
    engine = start_engine()

    bills = pydantic.TypeAdapter(list[_Bill]).validate_json(path.read_text(encoding="utf8"))

    with Session(engine) as session:
        for bill in bills:
            _fill(session, bill)

        session.commit()


if __name__ == "__main__":
    run(pathlib.Path("bills.json"))
