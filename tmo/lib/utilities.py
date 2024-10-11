import typing

_unset = object()


def get_attr_item(obj: typing.Any, key: typing.Any, *, default: typing.Any = _unset) -> typing.Any:
    if hasattr(obj, key):
        return getattr(obj, key)
    try:
        return obj[key]
    except (KeyError, TypeError):
        if default is not _unset:
            return default

    raise KeyError(f"'{key}'")
