import typing

import pytest

from tmo.frontend import filters


def test_split():
    assert "first" == filters._split("first")
    assert "first" == filters._split("first second")
    assert "first" == filters._split("first second third")

    assert "" == filters._split("")


@pytest.mark.parametrize(("klass", "value"), (("is-currency-negative", -1), ("is-currency-zero", 0), ("", 1)))
def test_currency_class(klass: str, value: typing.Any):
    assert klass == filters.currency_class(value)
