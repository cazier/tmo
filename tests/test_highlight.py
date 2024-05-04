import logging
import os
import typing

import pytest

from tmo.db.highlight import _LOGGER_NAME, _SqlHandler, attach_handler, db_print

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
def test_db_print(data: typing.Any, expected: str, capsys: pytest.CaptureFixture) -> None:
    db_print(data)
    stdout: str = capsys.readouterr().out

    for expected_token, token in zip(expected.split(" "), stdout.split(" ")):
        assert token.startswith("\x1b[")
        assert expected_token.lower() in token


@pytest.mark.parametrize(
    ("logged", "expected"),
    (SQL_STATEMENT,),
    ids=("strings",),
)
def test_SqlHandler(logged: str | tuple[str, tuple[typing.Any]], expected: str, caplog: pytest.LogCaptureFixture):
    attach_handler()
    logger = logging.getLogger(_LOGGER_NAME)
    assert isinstance(logger.handlers[0], _SqlHandler)

    # This is needed to propagate the logger emits up to the root logger that pytest is attached to.
    # Unfortunately it means we also need to reassign the stream to /dev/null so as to not pollute the console when run with `-s`
    logger.propagate = True

    with open(os.devnull, "w") as null:
        logger.handlers[0].stream = null

        with caplog.at_level(logging.DEBUG, _LOGGER_NAME):
            logger.info(logged)

    for expected_token, token in zip(expected.split(" "), caplog.messages[-1].split(" ")):
        assert token.startswith("\x1b[")
        assert expected_token.lower() in token
