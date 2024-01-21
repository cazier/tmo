import logging
import sys
import typing

import rich
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.sql import SqlLexer

try:
    from sqlfmt.api import Mode, format_string

    _mode = Mode(fast=True, no_color=True, no_progressbar=True)

except ImportError:
    logger = logging.getLogger("uvicorn")
    logger.warning("Install the `shandy-sqlfmt` package to colorize SQL queries.")

    def format_string(source_string: str, mode: Mode) -> str:  # pylint: disable=unused-argument
        """Optional def if the shandy-sqlfmt package is not available."""
        return source_string


_LOGGER_NAME = "sqlalchemy.engine.Engine"


def attach_handler() -> None:
    """Attach the colorized (and optionally formatted) SQL handler to the SQLAlchemy engine logger."""
    logging.getLogger(_LOGGER_NAME).addHandler(_SqlHandler())


def db_print(values: typing.Any, **kwargs: typing.Any) -> None:
    """Wrapper around a regular print call that adds colorization (and optionally formatting) to the SQLAlchemy
    engine.

    Args:
        values (typing.Any): database statements
    """
    if not isinstance(values, str):
        values = str(values)

    print(highlight(format_string(values, mode=_mode), SqlLexer(), Terminal256Formatter()), **kwargs)


class _SqlHandler(logging.StreamHandler[typing.TextIO]):  # pylint: disable=too-few-public-methods
    def __init__(self, stream: None | typing.TextIO = None) -> None:
        if not stream:
            stream = sys.stdout

        self.__logger = logging.getLogger(_LOGGER_NAME)

        if self.__logger.propagate:
            self.__logger.propagate = False

        if self.__logger.handlers:
            self.__logger.handlers.clear()

        super().__init__(stream=stream)

    def emit(self, record: logging.LogRecord) -> None:
        if record.msg.startswith("[%s]"):
            if isinstance(record.args, tuple):
                if not getattr(record.args[-1], "params", False):
                    return

                rich.print(record.args[-1])
                return

        db_print(record.msg, end="")
