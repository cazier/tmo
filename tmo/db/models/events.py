import typing

from sqlalchemy import event

from . import Bill


@event.listens_for(Bill.date, "set")
def _update_bill_date(target: Bill, *_: typing.Any) -> None:
    if target.date:
        raise AttributeError("Cannot change the date on an existing row.")


# @event.listens_for(Bill.charges, "append")
# def _update_bill_total(target: Bill, value: Charge, *_: typing.Any):
#     target.total = sum((item.total for item in (*target.details, *target.charges, value)), start=decimal.Decimal("0"))

# @event.listens_for(Subscriber.bills, "append")
# def _update_subscriber_count(target: Subscriber, *_) -> None:
#     target.count = 1 + len(target.bills)
