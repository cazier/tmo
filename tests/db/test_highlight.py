# mypy: disable-error-code="no-untyped-def"
import importlib
import logging
import os
import secrets
import sys
import typing
import unittest.mock

import pytest

from tmo.db.highlight import _LOGGER_NAME, _SqlHandler, attach_handler, db_print
from tmo.db.highlight_fallback import format_string, highlight

SQL_STATEMENT = ("SELECT * FROM users WHERE users.id=15", "select * from users where users.id = 15")


def test_attach_handler() -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    logger.handlers.clear()
    assert not logger.handlers

    attach_handler()
    assert logger.handlers and isinstance(logger.handlers[0], _SqlHandler)


@pytest.mark.parametrize(
    ("data", "expected"),
    (
        SQL_STATEMENT,
        (123, "123"),
    ),
    ids=("strings", "other"),
)
@pytest.mark.parametrize("capture", (True, False), ids=("string", "stdout"))
def test_db_print(capture: bool, data: str | int, expected: str, capsys: pytest.CaptureFixture[str]) -> None:
    if capture:
        stdout = db_print(data, capture=capture)

    else:
        db_print(data, capture=capture)
        stdout = capsys.readouterr().out

    for expected_token, token in zip(expected.split(" "), stdout.split(" ")):
        assert token.startswith("\x1b[")
        assert expected_token.lower() in token


@pytest.mark.parametrize(
    ("logged", "expected"),
    (SQL_STATEMENT,),
    ids=("strings",),
)
def test_sql_handler(logged: str, expected: str, caplog: pytest.LogCaptureFixture):
    attach_handler()
    logger = logging.getLogger(_LOGGER_NAME)
    assert isinstance(logger.handlers[0], _SqlHandler)

    # This is needed to propagate the logger emits up to the root logger that pytest is attached to.
    # Unfortunately it means we also need to reassign the stream to /dev/null so as to not pollute
    # the console when run with `-s`
    logger.propagate = True

    with open(os.devnull, "w", encoding="utf8") as null:
        logger.handlers[0].stream = null

        with caplog.at_level(logging.DEBUG, _LOGGER_NAME):
            logger.info(logged)

    for expected_token, token in zip(expected.split(" "), caplog.messages[-1].split(" ")):
        assert token.startswith("\x1b[")
        assert expected_token.lower() in token


class _TestObject:
    params: bool = True

    def __repr__(self) -> str:
        return "_TestObject"


@pytest.mark.parametrize(
    ("msg", "args", "expected"),
    (
        ("[%s] %r", ("raw sql", tuple()), "[raw sql] ()"),
        ("[%s] %r", ("", _TestObject()), "_testobject"),
    ),
    ids=("raw sql", "batch"),
)
def test_handler_ignores(msg: str, args: tuple[typing.Any], expected: str, caplog: pytest.LogCaptureFixture):
    attach_handler()
    logger = logging.getLogger(_LOGGER_NAME)
    assert isinstance(logger.handlers[0], _SqlHandler)

    # This is needed to propagate the logger emits up to the root logger that pytest is attached to.
    # Unfortunately it means we also need to reassign the stream to /dev/null so as to not pollute
    # the console when run with `-s`
    logger.propagate = True

    with open(os.devnull, "w", encoding="utf8") as null:
        logger.handlers[0].stream = null

        with caplog.at_level(logging.DEBUG, _LOGGER_NAME):
            logger.info(msg, *args)

    actual = caplog.messages[-1]
    assert not actual.startswith("\x1b[")
    assert actual == expected


class TestMissingImports:
    @pytest.mark.parametrize(
        ("name", "module"), (("pygments", "pygments"), ("shandy-sqlfmt", "sqlfmt.api")), ids=("pygments", "sqlfmt")
    )
    def test_import_catching(self, name: str, module: str, caplog: pytest.LogCaptureFixture):
        with unittest.mock.patch.dict(sys.modules):
            sys.modules[module] = None  # type: ignore[assignment]
            importlib.reload(sys.modules["tmo.db.highlight"])

        with caplog.at_level(logging.WARNING, "uvicorn"):
            assert f"Install the `{name}` package to" in caplog.text
            caplog.clear()

    def test_pygments_fallback(self):
        data = secrets.token_hex()

        assert data == highlight(data)

    def test_sqlfmt_fallback(self):
        data = secrets.token_hex()

        assert data == format_string(data)
