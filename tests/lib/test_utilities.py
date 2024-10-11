# mypy: disable-error-code="no-untyped-def"

import secrets
import typing

import pytest

from tmo.lib.utilities import get_attr_item


class _TestObject:
    hello: str

    def __init__(self, hello: str):
        self.hello = hello


@pytest.mark.parametrize("obj", ({"hello": "world"}, _TestObject("world")), ids=("map", "object"))
@pytest.mark.parametrize("success", (True, False, None), ids=("success", "failure", "default"))
def test_get_attr_item(obj: dict[str, typing.Any] | _TestObject, success: bool | None):
    if success is True:
        assert get_attr_item(obj, "hello") == "world"

    if success is False:
        key = secrets.token_hex(4)
        with pytest.raises(KeyError, match=rf"\'{key}\'"):
            get_attr_item(obj, key)

    if success is None:
        key = secrets.token_hex(4)
        default = secrets.token_hex(4)
        assert get_attr_item(obj, key, default=default) == default
