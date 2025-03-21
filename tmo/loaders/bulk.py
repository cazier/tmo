import datetime
import decimal
import pathlib

import httpx
import pydantic
from sqlmodel import Session

from tmo import config
from tmo.db.engines import start_engine
from tmo.db.models import Bill, Charge, Detail, Subscriber
from tmo.loaders.models import Bill as _Bill

_bill_cache: dict[datetime.date, Bill] = {}
_user_cache: dict[str, Subscriber] = {}


class _NameMap:
    def __init__(self, names: dict[str, str]) -> None:
        self._names = names

    def __getitem__(self, key: str) -> str:
        return self._names.get(key, self._names["default"])


def _fill_to_sql(session: Session, bill: _Bill) -> None:
    _name_map = _NameMap(config.load.names)
    _bill = _bill_cache.setdefault(bill.date, Bill(date=bill.date))

    for charge in bill.charges:
        _charge = Charge(name=charge.name, total=charge.total, split=charge.split, bill=_bill)
        session.add(_charge)

    for _data in bill.subscribers:
        surname = _name_map[_data.name]
        name = _data.name + " " + surname
        user = _user_cache.setdefault(_data.number, Subscriber(name=name, number=_data.number))
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
            _fill_to_sql(session, bill)

        session.commit()


@pydantic.validate_call
def api(data: pathlib.Path | _Bill) -> bool:
    if isinstance(data, pathlib.Path):
        data = _Bill.model_validate_json(data.read_text(encoding="utf8"))

    with httpx.Client(base_url="http://127.0.0.1:8000") as client:
        resp = client.post("/api/fill", json=data.model_dump(mode="json"))

    return resp.is_success


if __name__ == "__main__":
    run(pathlib.Path("bills.json"))
