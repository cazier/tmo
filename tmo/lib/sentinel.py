import contextlib
import typing

import pydantic

_UPDATE_SENTINEL = True
_sentinel: typing.Optional["Sentinel"] = None

P = typing.ParamSpec("P")


class Sentinel(pydantic.BaseModel):
    def __init__(self, *args: P.args, **kwargs: P.kwargs):
        global _UPDATE_SENTINEL, _sentinel

        super().__init__(*args, **kwargs)

        if _UPDATE_SENTINEL or _sentinel is None:
            _sentinel = self.model_copy(deep=True)

        _UPDATE_SENTINEL = False

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
    @contextlib.contextmanager
    def update_sentinel() -> typing.Generator[None, None, None]:
        global _UPDATE_SENTINEL

        _UPDATE_SENTINEL = True
        yield
        _UPDATE_SENTINEL = False

    @staticmethod
    def purge_sentinel() -> None:
        global _sentinel, _UPDATE_SENTINEL

        _sentinel = None
        _UPDATE_SENTINEL = True
