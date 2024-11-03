# mypy: disable-error-code="no-untyped-def"
import datetime

import faker
import pytest
from sqlmodel import Session, func, select

import tests.helpers
from tmo.db.models import Bill, Subscriber


@pytest.fixture
def subscriber(session: Session) -> Subscriber:
    instance = Subscriber(**tests.helpers.subscriber())
    session.add(instance)
    session.commit()

    return instance


@pytest.fixture
def bill(session: Session) -> Bill:
    instance = Bill(**tests.helpers.bill())
    session.add(instance)
    session.commit()

    return instance


class TestSubscriber:
    def test_add_subscriber(self, session: Session):
        subscriber = tests.helpers.subscriber()
        assert session.exec(select(Subscriber).where(Subscriber.number == subscriber["number"])).first() is None

        session.add(Subscriber(**subscriber))
        db_subscriber = session.exec(select(Subscriber).where(Subscriber.number == subscriber["number"])).one()

        assert subscriber == db_subscriber.model_dump()

    def test_delete_subscriber(self, subscriber: Subscriber, session: Session):
        rows = session.exec(select(func.count()).select_from(Subscriber)).one()
        db_subscriber = session.exec(select(Subscriber).where(Subscriber.number == subscriber.number)).one()

        session.delete(db_subscriber)
        session.commit()

        assert session.exec(select(func.count()).select_from(Subscriber)).one() < rows

    def test_edit_subscriber(self, subscriber: Subscriber, session: Session, faker: faker.Faker):
        db_subscriber = session.exec(select(Subscriber).where(Subscriber.number == subscriber.number)).one()
        db_subscriber.name = (name := faker.name())

        session.add(db_subscriber)
        session.commit()

        updated = session.get_one(Subscriber, db_subscriber.id)
        assert updated.name == name


class TestBill:
    def test_add_bill(self, bills: set[datetime.date], session: Session):
        bill = tests.helpers.bill()
        assert session.exec(select(Bill).where(Bill.date == bill["date"])).first() is None

        session.add(Bill(**bill))
        db_bill = session.exec(select(Bill).where(Bill.date == bill["date"])).one()

        assert bill == db_bill.model_dump()

    def test_delete_bill(self, bill: Bill, session: Session):
        rows = session.exec(select(func.count()).select_from(Bill)).one()
        db_bill = session.exec(select(Bill).where(Bill.date == bill.date)).one()

        session.delete(db_bill)
        session.commit()

        assert session.exec(select(func.count()).select_from(Bill)).one() < rows

    def test_edit_bill_date(self, bill: Bill, session: Session, faker: faker.Faker):
        db_bill = session.exec(select(Bill).where(Bill.date == bill.date)).one()

        with pytest.raises(AttributeError, match=r"(?i)Cannot change the date.*"):
            db_bill.date = faker.date_object()

        session.add(db_bill)
        session.commit()

        updated = session.get_one(Bill, db_bill.id)
        assert updated.date == bill.date

    def test_edit_bill_subscriber(self, subscriber: Subscriber, bill: Bill, session: Session, faker: faker.Faker):
        db_bill = session.exec(select(Bill).where(Bill.date == bill.date)).one()
        db_bill.subscribers.append(subscriber)

        session.add(db_bill)
        session.commit()

        updated = session.get_one(Bill, db_bill.id)
        assert updated.subscribers[0].name == subscriber.name
