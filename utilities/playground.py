from sqlalchemy.orm.mapper import Mapper
from sqlalchemy import Connection, select as sa_select
from sqlalchemy.orm import column_property, declared_attr, aliased, LoaderCallableStatus, attributes
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import ColumnElement, Integer, event, Float
from sqlmodel import SQLModel, create_engine, Session, Field, Relationship, select, func, type_coerce
from pydantic import ConfigDict, BaseModel
from tmo.db.highlight import LOGGER_NAME, SqlHandler
import decimal

from rich import print as pprint
import IPython

import typing
import logging
import itertools

logging.basicConfig()
logging.getLogger(LOGGER_NAME).addHandler(SqlHandler())

_T = typing.TypeVar("_T")

def print(*objects, **kwargs):
    return pprint('>>>', *objects, **kwargs)

class _CanStepThroughFields(SQLModel):
    @typing.overload
    def _fields_by_annotation(self, string: str) -> str:
        ...

    @typing.overload
    def _fields_by_annotation(self, klass: type[_T]) -> _T:
        ...

    def _fields_by_annotation(
        self, *, string: str = "", klass: typing.Optional[type[_T]] = None
    ) -> tuple[str, str | _T]:
        for name, field in itertools.chain(self.model_fields.items(), self.model_computed_fields.items()):
            for item in getattr(field, "metadata", getattr(getattr(field, "return_type", None), "__metadata__", [])):
                if klass and isinstance(item, klass):
                    yield name, item
                elif isinstance(item, str) and item == string:
                    yield name, item


class _User_Bill_Link(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)


class User(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)

    name: str
    total: typing.Annotated[int, "$"] = Field(default=0)

    details: list["Detail"] = Relationship(back_populates="user")
    bills: list["Bill"] = Relationship(back_populates="users", link_model=_User_Bill_Link)


class Charge(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)

    name: str
    total: typing.Annotated[int, "$"] = Field(default=0)

    bill: "Bill" = Relationship(back_populates="charges")
    bill_id: typing.Optional[int] = Field(default=None, foreign_key="bill.id")


class Detail(_CanStepThroughFields, SQLModel, table=True):
    model_config = ConfigDict(ignored_types=(declared_attr,hybrid_property))
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    phone: typing.Annotated[int, "$"] = Field(default=0)
    line: typing.Annotated[decimal.Decimal, "$"] = Field(default=0, max_digits=5, decimal_places=2)

    total: decimal.Decimal = Field(default=0, max_digits=5, decimal_places=2)

    # @hybrid_property
    # def total(self) -> decimal.Decimal:
    #     return self.phone + self.line

    user: "User" = Relationship(back_populates="details")
    user_id: typing.Optional[int] = Field(default=None, foreign_key="user.id")

    bill: "Bill" = Relationship(back_populates="details")
    bill_id: typing.Optional[int] = Field(default=None, foreign_key="bill.id")


class Bill(SQLModel, table=True):
    # model_config = ConfigDict(ignored_types=(declared_attr, ))
    # model_config = ConfigDict(validate_assignment=True)

    id: typing.Optional[int] = Field(default=None, primary_key=True)

    total: decimal.Decimal =  Field(default=0, decimal_places=2, max_digits=8)
    # total: typing.ClassVar[decimal.Decimal] = hybrid_property(lambda k:sum(detail.total for detail in k.details) + sum(charge.total for charge in k.charges) )

    # @hybrid_property
    # def total(self) -> decimal.Decimal:
    #     return sum(detail.total for detail in self.details) + sum(charge.total for charge in self.charges)
    
    # @total.inplace.expression
    # @classmethod
    # def _total_expression(cls) -> ColumnElement[decimal.Decimal]:
    #     return type_coerce(func.sum(cls.details.total, cls.id == Detail.bill_id), Float)


    users: list["User"] = Relationship(back_populates="bills", link_model=_User_Bill_Link)
    details: list["Detail"] = Relationship(back_populates="bill")
    charges: list["Charge"] = Relationship(back_populates="bill")


# @event.listens_for(Bill.charges, 'append')
# @event.listens_for(Bill.details, "append")
# def _update_bill(target: Bill, value: Detail, *_):
#     target.total += value.total

# @event.listens_for(Detail.line, 'modified')
# @event.listens_for(Detail.phone, 'modified')
# @event.listens_for(Charge.total, 'modified')
# # @listens_for('set', Detail.line, Detail.phone, Detail.total)
# # def _update_detail(target: Detail | Charge, value: typing.Any, oldvalue: decimal.Decimal, initiator: attributes.AttributeEventToken) -> int:
# def _update_detail(target: Detail | Charge, initiator: attributes.AttributeEventToken) -> int:
#     breakpoint()

#     return
#     if oldvalue != LoaderCallableStatus.NO_VALUE:
#         value = decimal.Decimal(value) - oldvalue
#         target.bill.total += value

#     if isinstance(target, Charge):
#         return

    # target.total = value + sum(getattr(target, name) or 0 for name, _ in target._fields_by_annotation(string='$'))

# @event.listens_for(Session, 'before_flush')
# def receive_before_flush(session, flush_context, instances):
#     IPython.embed()


@event.listens_for(Detail, "init")
def _update_bill_total(target: Detail, args: typing.Any, kwargs: dict[str, typing.Any]):
    kwargs.setdefault("total", sum(kwargs.get(key, 0) for key, _ in target._fields_by_annotation(string="$")))


engine = create_engine("sqlite://", echo=True)


def _setup():
    SQLModel.metadata.create_all(engine)


def _models():
    with Session(engine) as session:
        bill = Bill()
        user1 = User(name="First User")
        user2 = User(name="Second User")

        d1 = Detail(phone=12, line=30.0, user_id=user1.id, bill_id=bill.id)
        d2 = Detail(phone=40, line=40.0, user_id=user2.id, bill_id=bill.id)

        charges = Charge(name="netflix", total=34, bill_id=bill.id)

        bill.users.extend([user1, user2])
        bill.charges.append(charges)
        bill.details.extend([d1, d2])
        user1.details.append(d1)
        user2.details.append(d2)

        session.add_all((user1, user2, d1, d2, bill, charges))

        session.commit()

        bill = session.exec(select(Bill)).first()
        user1, user2 = session.exec(select(User)).all()
        detail1, detail2 = session.exec(select(Detail)).all()
        charges = session.exec(select(Charge)).first()

        # print(bill)
        # print(user1)
        # print(user2)
        # print(detail1)
        # print(detail2)
        # print(detail2.total)
        # print(charges)
        print('pause')
        print(select(bill.total))
        # print(bill.total)
        return
    
        detail1.line = 92.0
        charges.total += 15

        # charges.total = 94
        # session.add(charges)
        # session.commit()

        bill = session.exec(select(Bill)).first()
        details = session.exec(select(Detail)).all()
        charges = session.exec(select(Charge)).all()
        print(details)
        print(charges)
        print(bill)
        # print(bill.total)

        # total = session.exec(select(Bill.total).where(Bill.id == 1)).first()

        # print(total)

        # IPython.start_ipython(argv=[], user_ns=locals())


def main():
    _setup()
    _models()


# main()
