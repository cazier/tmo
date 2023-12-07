import datetime
import decimal
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class _Subscriber_Bill_Link(SQLModel, table=True):
    subscriber_id: int = Field(foreign_key="subscriber.id", primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", primary_key=True)


class _Charges_Statistics_Link(SQLModel, table=True):
    charges_id: int = Field(foreign_key="charges.id", primary_key=True)
    statistics_id: int = Field(foreign_key="statistics.id", primary_key=True)


class _BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


class Subscriber(_BaseModel, table=True):
    name: str
    number: str = Field(unique=True, max_length=20)
    number_format: str = Field(default="us", max_length=2)

    charges: list["Charges"] = Relationship(back_populates="subscriber")
    statistics: list["Statistics"] = Relationship(back_populates="subscriber")

    bills: list["Bill"] = Relationship(back_populates="subscribers", link_model=_Subscriber_Bill_Link)


class Bill(_BaseModel, table=True):
    date: datetime.date = Field(unique=True)

    charges: list["Charges"] = Relationship(back_populates="bill")
    statistics: list["Statistics"] = Relationship(back_populates="bill")

    subscribers: list["Subscriber"] = Relationship(back_populates="bills", link_model=_Subscriber_Bill_Link)


class Charges(_BaseModel, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="charges")

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: Subscriber = Relationship(back_populates="charges")

    line: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2)
    phone: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2)
    usage: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2)
    insurance: decimal.Decimal = Field(default=0, max_digits=8, decimal_places=2)

    statistics: "Statistics" = Relationship(
        back_populates="charges",
        sa_relationship_kwargs={"uselist": False},
        link_model=_Charges_Statistics_Link,
    )


class Statistics(_BaseModel, table=True):
    bill_id: int = Field(foreign_key="bill.id")
    bill: Bill = Relationship(back_populates="statistics")

    subscriber_id: int = Field(foreign_key="subscriber.id")
    subscriber: Subscriber = Relationship(back_populates="statistics")

    minutes: Optional[int] = Field(default=0)
    messages: Optional[int] = Field(default=0)
    data: decimal.Decimal = Field(default=0, max_digits=5, decimal_places=2)

    charges: "Charges" = Relationship(
        back_populates="statistics",
        sa_relationship_kwargs={"uselist": False},
        link_model=_Charges_Statistics_Link,
    )
