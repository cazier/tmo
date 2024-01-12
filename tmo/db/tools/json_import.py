import datetime
import json
import pathlib
import typing

from sqlmodel import Session

from tmo.config import load
from tmo.db.engines import engine
from tmo.db.models import Bill, Charge, Detail, Subscriber


class _SubscriberImport(typing.TypedDict):
    name: str
    num: str

    minutes: int
    messages: int
    data: float

    phone: float
    line: float
    insurance: float
    usage: float


class _Import(typing.TypedDict):
    subscribers: _SubscriberImport
    other: dict[str, float]


_bill_cache: dict[datetime.date, Bill] = {}
_user_cache: dict[str, Subscriber] = {}


class _NameMap:  # pylint: disable=too-few-public-methods
    def __init__(self, names: dict[str, str]) -> None:
        self._names = names

    def __getitem__(self, key: str) -> str:
        return self._names.get(key, self._names["default"])


_name_map = _NameMap(load["names"])


def _load(path: pathlib.Path) -> dict[str, _Import]:
    return typing.cast(dict[str, _Import], json.loads(path.read_text(encoding="utf-8")))


def _fill(session: Session, date: str | datetime.date, data: _Import) -> None:
    if isinstance(date, str):
        date = datetime.date(*map(int, date.split(".")))

    bill = _bill_cache.setdefault(date, Bill(date=date))

    for kind, total in data["other"].items():
        charge = Charge(name=kind, total=total, bill=bill)
        session.add(charge)

    for _data in data["subscribers"]:
        surname = _name_map[_data["name"]]
        name = _data["name"] + " " + surname
        user = _user_cache.setdefault(_data["num"], Subscriber(name=name, number=_data["num"]))
        user.bills.append(bill)

        detail = Detail(
            bill=bill,
            subscriber=user,
            phone=_data["phone"],
            line=_data["line"],
            insurance=_data["insurance"],
            usage=_data["usage"],
            minutes=_data["minutes"],
            messages=_data["messages"],
            data=_data["data"],
        )
        session.add(detail)

    session.add(bill)
    session.add(user)


def run(path: pathlib.Path) -> None:
    bills = _load(path)

    with Session(engine) as session:
        for date, user in bills.items():
            _fill(session, date, user)

        session.commit()


if __name__ == "__main__":
    run(pathlib.Path("bills.json"))
