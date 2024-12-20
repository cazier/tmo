# mypy: disable-error-code="no-untyped-def"

import secrets
import typing
from types import SimpleNamespace as NS

import pytest

from tmo.lib.utilities import get_attr_item


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
