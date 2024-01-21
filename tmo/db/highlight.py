import logging
import sys
import typing

import rich

try:
    from pygments import highlight
    from pygments.formatters.terminal256 import Terminal256Formatter
    from pygments.lexers.sql import SqlLexer
    from sqlfmt.api import Mode, format_string

    _COLORIZATION = True

    _mode = Mode(fast=True, no_color=True, no_progressbar=True)


except ImportError:
    logging.getLogger(__name__).warning("Install the `shandy-sqlfmt` package to colorize SQL queries.")

    _COLORIZATION = False

LOGGER_NAME = "sqlalchemy.engine.Engine"


def attach_handler() -> None:
    logging.getLogger(LOGGER_NAME).addHandler(_SqlHandler())


def db_print(values: typing.Any, **kwargs: typing.Any) -> None:
    if not isinstance(values, str):
        values = str(values)

    if _COLORIZATION:
        print(highlight(format_string(values, mode=_mode), SqlLexer(), Terminal256Formatter()), **kwargs)

    else:
        print(values, **kwargs)


class _SqlHandler(logging.StreamHandler[typing.TextIO]):  # pylint: disable=too-few-public-methods
    def __init__(self, stream: None | typing.TextIO = None) -> None:
        if not stream:
            stream = sys.stdout

        self.__logger = logging.getLogger(LOGGER_NAME)

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
