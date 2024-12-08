import collections
import decimal
import random
import typing

import faker as _faker

faker = _faker.Faker()


class CompareDict(collections.UserDict[str, typing.Any]):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, typing.Mapping):
            return False

        return super().__eq__({key: value for key, value in other.items() if key != "id"})


def phone_number() -> str:
    return f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}-{random.randint(0, 9999):04d}"


def bill() -> CompareDict:
    return CompareDict({"date": faker.date_between(), "total": decimal.Decimal(faker.random_number(digits=5)) / 100})
