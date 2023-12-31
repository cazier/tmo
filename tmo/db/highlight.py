import logging
import sys
import typing

import rich
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.sql import SqlLexer

LOGGER_NAME = "sqlalchemy.engine.Engine"


def db_print(values: typing.Any, **kwargs: typing.Any) -> None:
    if not isinstance(values, str):
        values = str(values)

    print(highlight(values, SqlLexer(), Terminal256Formatter()), **kwargs)


class SqlHandler(logging.StreamHandler[typing.TextIO]):  # pylint: disable=too-few-public-methods
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