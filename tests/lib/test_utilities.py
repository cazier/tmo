# mypy: disable-error-code="no-untyped-def"

import datetime
import secrets
import typing
from types import SimpleNamespace as NS

import pytest
import time_machine

from tmo.lib.utilities import generate_totp, get_attr_item


@pytest.mark.parametrize(
    ("object", "key", "value"),
    (
        ({"a": "world"}, ("a",), "world"),
        ({"a": {"b": "world"}}, ("a", "b"), "world"),
        (NS(a="world"), ("a",), "world"),
        (NS(a=NS(b="world")), ("a", "b"), "world"),
        ({"a": NS(b="world")}, ("a", "b"), "world"),
        (NS(a={"b": "world"}), ("a", "b"), "world"),
        ({"a": NS(a={"b": "world"})}, ("a", "a", "b"), "world"),
        ({"a": {"b": None}}, ("a", "b"), None),
    ),
    ids=("map", "map-map", "object", "object-object", "map-object", "object-map", "map-object-map", "none-value"),
)
@pytest.mark.parametrize("success", (True, False, None), ids=("success", "failure", "default"))
def test_get_attr_item(
    object: dict[str, typing.Any] | NS, key: tuple[str, ...], value: typing.Any, success: bool | None
):
    if success is True:
        assert get_attr_item(object, *key) == value

    if success is False:
        key = (secrets.token_hex(4),)
        with pytest.raises(KeyError):
            get_attr_item(object, *key)

    if success is None:
        key = (secrets.token_hex(4),)
        default = secrets.token_hex(4)
        assert get_attr_item(object, *key, default=default) == default


@pytest.mark.parametrize(
    ("secret", "token", "digits"),
    [
        ("G6VQ6WTFLJZBQ3B4SUTZZY74OK25U7OY", "3106", 4),
        ("7ST7I24ILYL243RT44KHI5LHHZR75RNQ", "328032", 6),
        ("LDZIOQW4EGXSIRZNSIV3XHEPAW2OZKYN", "001943946416", 12),
    ],
    ids=("4 digits", "6 digits", "12 digits"),
)
def test_generate(secret: str, token: str, digits: int, time_machine: time_machine.TimeMachineFixture):
    time_machine.move_to(datetime.datetime(2011, 10, 9, 8, 7, 6))
    assert generate_totp(secret=secret, digits=digits) == token
