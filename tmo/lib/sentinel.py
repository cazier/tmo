import contextlib
import typing

import pydantic

_update_self = True  # pylint: disable=invalid-name
_sentinel: typing.Optional["Sentinel"] = None

P = typing.ParamSpec("P")


class Sentinel(pydantic.BaseModel):
    # pylint: disable=global-statement
    @staticmethod
    @contextlib.contextmanager
    def update_self() -> typing.Generator[None, None, None]:
        global _update_self

        _update_self = True
        yield
        _update_self = False

    def __init__(self, *args: P.args, **kwargs: P.kwargs):
        global _update_self, _sentinel

        super().__init__(*args, **kwargs)

        if _update_self or _sentinel is None:
            _sentinel = self.model_copy(deep=True)

        _update_self = False

    def __getattribute__(self, name: str) -> typing.Any:
        if name in "model_fields" or name not in type(self).model_fields:
            return super().__getattribute__(name)

        return object.__getattribute__(_sentinel, name)

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name not in type(self).model_fields:
            return object.__setattr__(self, name, value)

        return object.__setattr__(_sentinel, name, value)

    def __repr__(self) -> str:
        fields = ", ".join(f"{field}={repr(getattr(self, field))}" for field in self.model_fields)
        return f"{type(self).__name__}({fields})"

    def __str__(self) -> str:
        return self.__repr__()

    def __rich__(self) -> str:
        return self.__repr__()

    @staticmethod
    def purge_sentinel() -> None:
        global _sentinel, _update_self

        _sentinel = None
        _update_self = True
