import base64
import hashlib
import hmac
import struct
import time
import typing

import sqlalchemy.orm.attributes

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

    return get_attr_item(result, *_others, default=default)


T = typing.TypeVar("T")


def cast_as_qa(item: T) -> sqlalchemy.orm.attributes.QueryableAttribute[T]:
    return typing.cast(sqlalchemy.orm.attributes.QueryableAttribute[T], item)


def generate_totp(secret: str, digits: int = 6, interval: int = 30) -> str:
    counter = int(time.time() // interval)

    hmac_hash = hmac.digest(
        key=base64.b32decode(secret, casefold=True),
        msg=struct.pack(">Q", counter),
        digest=hashlib.sha1,
    )

    offset = hmac_hash[-1] & 0x0F
    binary_code = struct.unpack(">I", hmac_hash[offset : offset + 4])[0] & 0x7FFFFFFF

    totp_code = binary_code % (10**digits)
    return str(totp_code).zfill(digits)
