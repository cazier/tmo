import datetime
import json
import pathlib
import typing

from sqlmodel import Session

from tmo.config import load
from tmo.db.engines import engine
from tmo.db.models import Bill, Charges, Statistics, Subscriber


class _Import(typing.TypedDict):
    name: str
    num: str

    minutes: int
    messages: int
    data: float

    phone: float
    line: float
    insurance: float
    usage: float


_bill_cache: dict[datetime.date, Bill] = {}
_user_cache: dict[str, Subscriber] = {}


class _NameMap:  # pylint: disable=too-few-public-methods
    def __init__(self, names: dict[str, str]) -> None:
        self._names = names

    def __getitem__(self, key: str) -> str:
        return self._names.get(key, self._names["default"])


_name_map = _NameMap(load["names"])


def _load(path: pathlib.Path) -> dict[str, list[_Import]]:
    return typing.cast(dict[str, list[_Import]], json.loads(path.read_text(encoding="utf-8")))


def _fill(session: Session, date: str | datetime.date, data: list[_Import]) -> None:
    if isinstance(date, str):
        date = datetime.date(*map(int, date.split(".")))

    bill = _bill_cache.setdefault(date, Bill(date=date))

    for _data in data:
        surname = _name_map[_data["name"]]
        name = _data["name"] + " " + surname
        user = _user_cache.setdefault(_data["num"], Subscriber(name=name, number=_data["num"]))
        user.bills.append(bill)

        charges = Charges(
            bill=bill,
            subscriber=user,
            phone=_data["phone"],
            line=_data["line"],
            insurance=_data["insurance"],
            usage=_data["usage"],
        )

        stats = Statistics(
            bill=bill,
            subscriber=user,
            minutes=_data["minutes"],
            messages=_data["messages"],
            data=_data["data"],
            charges=charges,
        )

        charges.statistics = stats

        session.add(stats)
        session.add(charges)

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
