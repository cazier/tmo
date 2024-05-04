import logging
import sys
import typing

try:
    from pygments import highlight
    from pygments.formatters.terminal256 import Terminal256Formatter
    from pygments.lexers.sql import SqlLexer

except ImportError:  # pragma: nocover
    # pylint: disable=invalid-name
    logger = logging.getLogger("uvicorn")
    logger.warning("Install the `pygments` package to colorize SQL queries.")

    def highlight(value: typing.Any) -> str:  # type: ignore[no-redef]
        """Optional def if the pygments package is not available."""
        return str(value)

    def Terminal256Formatter() -> None:  # type: ignore[no-redef]
        """Optional def if the pygments package is not available."""
        return None

    def SqlLexer() -> None:  # type: ignore[no-redef]
        """Optional def if the pygments package is not available."""
        return None


try:
    from sqlfmt.api import Mode, format_string

    _mode = Mode(fast=True, no_color=True, no_progressbar=True)

except ImportError:  # pragma: nocover
    logger = logging.getLogger("uvicorn")
    logger.warning("Install the `shandy-sqlfmt` package to format SQL queries.")

    def format_string(source_string: str, mode: Mode) -> str:  # pylint: disable=unused-argument
        """Optional def if the shandy-sqlfmt package is not available."""
        return source_string


_LOGGER_NAME = "sqlalchemy.engine.Engine"


def attach_handler() -> None:
    """Attach the colorized (and optionally formatted) SQL handler to the SQLAlchemy engine logger."""
    logging.getLogger(_LOGGER_NAME).addHandler(_SqlHandler())


@typing.overload
def db_print(values: typing.Any, capture: typing.Literal[True], **kwargs: typing.Any) -> str: ...  # pragma: nocover


@typing.overload
def db_print(values: typing.Any, capture: typing.Literal[False], **kwargs: typing.Any) -> None: ...  # pragma: nocover


def db_print(values: typing.Any, capture: bool = False, **kwargs: typing.Any) -> None | str:
    """Wrapper around a regular print call that adds colorization (and optionally formatting) to the SQLAlchemy
    engine.

    Args:
        values (typing.Any): database statements
        capture (bool, optional): capture and return the colored/formatted values Defaults to False.

    Returns:
        str | None: captured pretty values (if `capture` is set to True)
    """
    if not isinstance(values, str):
        values = str(values)

    formatted = highlight(format_string(values, mode=_mode), SqlLexer(), Terminal256Formatter())

    if capture:
        return formatted

    return print(formatted, **kwargs)


class _SqlHandler(logging.StreamHandler[typing.TextIO]):  # pylint: disable=too-few-public-methods
    def __init__(self, stream: None | typing.TextIO = None) -> None:
        stream = stream or sys.stdout

        self.__logger = logging.getLogger(_LOGGER_NAME)
        self.__logger.propagate = False
        self.__logger.handlers.clear()

        super().__init__(stream=stream)

    def emit(self, record: logging.LogRecord) -> None:
        """Colorize/format (if able) the logging message and/or arguments.

        Args:
            record (logging.LogRecord): logging entry
        """
        if record.msg.startswith("[%s]"):
            if isinstance(record.args, tuple):
                if not getattr(record.args[-1], "params", False):
                    return

                record.msg = record.args[-1]
                record.args = tuple()

        record.msg = db_print(record.msg, capture=True).rstrip()

        super().emit(record)
