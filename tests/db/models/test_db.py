# pylint: disable=not-callable
# mypy: disable-error-code="no-untyped-def"

from sqlmodel import Session, func, select

from tmo.db.models import Subscriber


def test_add_subscriber(subscribers: list[dict[str, str]], session: Session):
    [subscriber, *_] = subscribers

    assert session.exec(select(func.count()).select_from(Subscriber)).first() == 0

    session.add(Subscriber(**subscriber))
    db_subscriber = session.get_one(Subscriber, 1)

    assert session.exec(select(func.count()).select_from(Subscriber)).first() == 1
    assert db_subscriber.id == 1
    assert db_subscriber.name == subscriber["name"]
    assert db_subscriber.number == subscriber["number"]


def test_delete_subscriber(subscribers: list[dict[str, str]], session: Session):
    [subscriber, *_] = subscribers
    session.add(Subscriber(**subscriber))
    session.commit()

    assert session.exec(select(func.count()).select_from(Subscriber)).first() == 1
    db_subscriber = session.get_one(Subscriber, 1)

    session.delete(db_subscriber)
    session.commit()

    assert session.exec(select(func.count()).select_from(Subscriber)).first() == 0
