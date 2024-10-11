# mypy: disable-error-code="no-untyped-def"

import secrets
import typing

import pytest

from tmo.lib.utilities import get_attr_item


class _TestObject:
    hello: typing.Any

    def __init__(self, hello: typing.Any):
        self.hello = hello


@pytest.mark.parametrize(
    ("obj", "key"),
    (
        ({"hello": "world"}, ("hello",)),
        ({"hello": {"goodbye": "world"}}, ("hello", "goodbye")),
        (_TestObject("world"), ("hello",)),
        (_TestObject(_TestObject("world")), ("hello", "hello")),
        ({"hello": _TestObject("world")}, ("hello", "hello")),
        (_TestObject({"goodbye": "world"}), ("hello", "goodbye")),
        ({"hello": _TestObject({"goodbye": "world"})}, ("hello", "hello", "goodbye")),
    ),
    ids=("map", "map-map", "object", "object-object", "map-object", "object-map", "map-object-map"),
)
@pytest.mark.parametrize("success", (True, False, None), ids=("success", "failure", "default"))
def test_get_attr_item(obj: dict[str, typing.Any] | _TestObject, key: tuple[str, ...], success: bool | None):
    if success is True:
        assert get_attr_item(obj, *key) == "world"

    if success is False:
        key = (secrets.token_hex(4),)
        with pytest.raises(KeyError, match=rf"\'{key}\'"):
            get_attr_item(obj, *key)

    if success is None:
        key = (secrets.token_hex(4),)
        default = secrets.token_hex(4)
        assert get_attr_item(obj, *key, default=default) == default
