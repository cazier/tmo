# mypy: disable-error-code="no-untyped-def"
import datetime

import pytest
from faker import Faker
from sqlmodel import Session, func, select

from tmo.db.models import Bill, Subscriber


@pytest.fixture
def subscriber(subscribers: list[dict[str, str]], session: Session) -> Subscriber:
    [subscriber, *_] = subscribers
    instance = Subscriber(**subscriber)
    session.add(instance)
    session.commit()

    return instance


@pytest.fixture
def bill(bills: set[datetime.date], session: Session) -> Bill:
    [date, *_] = list(bills)
    instance = Bill(date=date)
    session.add(instance)
    session.commit()

    return instance


class TestSubscriber:
    def test_add_subscriber(self, subscribers: list[dict[str, str]], session: Session):
        [subscriber, *_] = subscribers

        assert session.exec(select(func.count()).select_from(Subscriber)).first() == 0

        session.add(Subscriber(**subscriber))
        db_subscriber = session.get_one(Subscriber, 1)

        assert session.exec(select(func.count()).select_from(Subscriber)).first() == 1
        assert db_subscriber.id == 1
        assert db_subscriber.count == 0
        assert db_subscriber.name == subscriber["name"]
        assert db_subscriber.number == subscriber["number"]

    def test_delete_subscriber(self, subscriber: Subscriber, session: Session):
        db_subscriber = session.exec(select(Subscriber).where(Subscriber.name == subscriber.name)).one()

        session.delete(db_subscriber)
        session.commit()

        assert session.exec(select(func.count()).select_from(Subscriber)).first() == 0

    def test_edit_subscriber(self, subscriber: Subscriber, session: Session, faker: Faker):
        db_subscriber = session.exec(select(Subscriber).where(Subscriber.name == subscriber.name)).one()
        db_subscriber.name = (name := faker.name())

        session.add(db_subscriber)
        session.commit()

        updated = session.get(Subscriber, db_subscriber.id)
        assert updated.name == name


class TestBill:
    def test_add_bill(self, bills: set[datetime.date], session: Session):
        [date, *_] = list(bills)

        assert session.exec(select(func.count()).select_from(Bill)).first() == 0

        session.add(Bill(date=date))
        db_bill = session.get_one(Bill, 1)

        assert session.exec(select(func.count()).select_from(Bill)).first() == 1
        assert db_bill.id == 1
        assert db_bill.date == date

    def test_delete_bill(self, bill: Bill, session: Session):
        db_bill = session.exec(select(Bill).where(Bill.date == bill.date)).one()

        session.delete(db_bill)
        session.commit()

        assert session.exec(select(func.count()).select_from(Bill)).first() == 0

    def test_edit_bill_date(self, bill: Bill, session: Session, faker: Faker):
        db_bill = session.exec(select(Bill).where(Bill.date == bill.date)).one()

        with pytest.raises(AttributeError, match=r"(?i)Cannot change the date.*"):
            db_bill.date = faker.date_object()

        session.add(db_bill)
        session.commit()

        updated = session.get(Bill, db_bill.id)
        assert updated.date == bill.date

    def test_edit_bill_subscriber(self, subscriber: Subscriber, bill: Bill, session: Session, faker: Faker):
        db_bill = session.exec(select(Bill).where(Bill.date == bill.date)).one()
        db_bill.subscribers.append(subscriber)

        session.add(db_bill)
        session.commit()

        updated = session.get(Bill, db_bill.id)
        assert updated.subscribers[0].name == subscriber.name
