# mypy: disable-error-code="union-attr, no-untyped-def"
import typing

import pytest

from tmo.lib import sentinel

pytestmark = [pytest.mark.skip()]


class _TestObject(sentinel.Sentinel):
    a: str = "a"
    b: list[int] = []


@pytest.fixture(autouse=True)
def setup_teardown():
    sentinel.Sentinel.purge_sentinel()
    yield
    sentinel.Sentinel.purge_sentinel()


def test_access():
    _TestObject()
    assert sentinel._sentinel is not None


def test_purging():
    _TestObject()
    _TestObject.purge_sentinel()
    assert sentinel._sentinel is None


class TestUpdateProtection:
    def test_persistent_sentinel(self):
        _TestObject()
        initial = id(sentinel._sentinel)

        _TestObject()
        assert initial == id(sentinel._sentinel)

    def test_implicit_update(self):
        _TestObject()
        initial = id(sentinel._sentinel)

        _TestObject.purge_sentinel()
        _TestObject()

        assert initial != id(sentinel._sentinel)

    def test_explicit_update(self):
        _TestObject()
        initial = id(sentinel._sentinel)

        with _TestObject.update_sentinel():
            _TestObject()

        assert initial != id(sentinel._sentinel)


def test_get_attribute():
    instance = _TestObject(a="abc")
    duplicate = _TestObject(a="def")
    assert sentinel._sentinel.a == "abc"
    assert instance.a == "abc" and duplicate.a == "abc"

    reinstance = _TestObject(a="ghi")
    assert reinstance.a == "abc"


def test_set_attribute():
    instance = _TestObject(a="abc")
    duplicate = _TestObject(a="def")
    assert instance.a == "abc" and duplicate.a == "abc"

    instance.a = "def"
    assert instance.a == "def" and duplicate.a == "def"
    assert sentinel._sentinel.a == "def"


def test_set_mutable():
    instance = _TestObject(b=[1, 2])
    duplicate = _TestObject(b=[3])
    assert instance.b == [1, 2] and duplicate.b == [1, 2]

    instance.b.extend([3])

    assert instance.b == [1, 2, 3] and duplicate.b == [1, 2, 3]
    assert sentinel._sentinel.b == [1, 2, 3]


def test_set_unique_attributes():
    instance = _TestObject(a="abc")
    duplicate = _TestObject(a="def")
    assert instance.a == "abc" and duplicate.a == "abc"

    instance.__pydantic_extra__ = {"ghi": None}
    assert instance.__pydantic_extra__ == {"ghi": None} and duplicate.__pydantic_extra__ != {"ghi": None}


@pytest.fixture
def func(request: pytest.FixtureRequest) -> typing.Callable[[typing.Any], str]:
    match request.param:
        case "str":
            return str
        case "rich.print":
            return lambda k: k.__rich__()
        case _:
            return repr


@pytest.mark.parametrize("func", ("repr", "str", "rich.print"), indirect=True)
def test_displays(func: typing.Callable[[typing.Any], str]):
    instance = _TestObject(a="abc")
    duplicate = _TestObject(a="def")

    assert func(instance).replace('"', "___").replace("'", "___") == "_TestObject(a=___abc___, b=[])"
    assert func(instance) == func(duplicate)
