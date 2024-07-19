# pylint: disable=unused-argument,too-few-public-methods
import typing

P = typing.ParamSpec("P")


def highlight(code: str, *args: P.args, **kwargs: P.kwargs) -> str:
    """Optional def if the pygments package is not available."""
    return str(code)


class Terminal256Formatter:
    """Optional def if the pygments package is not available."""


class SqlLexer:
    """Optional def if the pygments package is not available."""


def format_string(source_string: str, *args: P.args, **kwargs: P.kwargs) -> str:
    """Optional def if the shandy-sqlfmt package is not available."""
    return source_string
