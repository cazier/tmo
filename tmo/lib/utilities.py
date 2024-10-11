import typing

_unset = object()


def get_attr_item(obj: typing.Any, *key: typing.Any, default: typing.Any = _unset) -> typing.Any:
    if not key:
        return obj

    _key, *_others = key

    if hasattr(obj, _key):
        result = getattr(obj, _key)

    else:
        try:
            result = obj[_key]

        except (KeyError, TypeError):
            if default is not _unset:
                return default

            raise KeyError(f"'{_key}'")

    if result is _unset:
        return default

    return get_attr_item(result, *_others, default=default)
