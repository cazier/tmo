import typing

from sqlalchemy import event

from . import Bill, Detail, Subscriber  # pylint: disable=cyclic-import


@event.listens_for(Bill.charges, "append")
@event.listens_for(Bill.details, "append")
def _update_bill_total(target: Bill, value: "Detail", *_) -> None:
    target.total = value.total + sum(item.total for item in target.details + target.charges)


@event.listens_for(Subscriber.bills, "append")
def _update_subscriber_count(target: Subscriber, *_) -> None:
    target.count = 1 + len(target.bills)


@event.listens_for(Detail, "init")
def _init_detail_total(target: Detail, _: tuple[typing.Any], kwargs: dict[str, typing.Any]):
    kwargs.setdefault("total", sum(kwargs[name] for name, _ in target.fields_by_annotation(string="$")))


# @event.listens_for(Detail.phone, "set")
# @event.listens_for(Detail.line, "set")
# @event.listens_for(Detail.insurance, "set")
# @event.listens_for(Detail.usage, "set")
# def _update_detail(target: Detail, value: JsonDecimal, oldvalue: JsonDecimal, *_):
#     if oldvalue != orm.LoaderCallableStatus.NO_VALUE:
#         value = value - oldvalue
#         target.bill.total += value

#     target.total = value + sum(getattr(target, name) or 0 for name, _ in target._fields_by_annotation(string="$"))
