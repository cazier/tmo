# mypy: disable-error-code="no-untyped-def"

import logging
import pathlib
import secrets
import unittest.mock

import pytest

from tmo import config
from tmo.db.engines import start_engine
from tmo.db.highlight import _LOGGER_NAME, _SqlHandler


@pytest.mark.parametrize("source", ("memory", "file"))
def test_sqlite_source(source: str, tmp_path: pathlib.Path):
    if source == "file":
        path = tmp_path.joinpath(secrets.token_hex())
        assert not path.exists()

        database = {"dialect": "sqlite", "path": path}

    else:
        path = None
        database = {"dialect": "memory"}

    with config.patch(database=database):
        engine = start_engine()
        assert engine.url.database in (path, str(path))


def test_postgres_source(monkeypatch: pytest.MonkeyPatch):
    name = secrets.token_hex()

    mock_engine = unittest.mock.Mock()
    mock_url = unittest.mock.Mock()

    mock_url.database = name
    mock_engine.url = mock_url
    mock_call = unittest.mock.Mock(return_value=mock_engine)

    database = {
        "dialect": "postgres",
        "username": "postgres",
        "password": "password",
        "database": name,
        "host": "localhost",
    }

    with config.patch(database=database):
        monkeypatch.setattr("tmo.db.engines._postgres.create_engine", mock_call)
        engine = start_engine()

        assert engine.url.database == name and mock_call.call_count == 1


def test_invalid_database_type(caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch):
    mock = unittest.mock.Mock()
    monkeypatch.setattr(config, "database", mock)
    with pytest.raises(SystemExit) as exc:
        start_engine()

    [message] = caplog.messages
    assert exc.type is SystemExit and exc.value.code == 1

    assert message == f"Could not match the database type: {type(mock)}"


def test_adding_echo(capsys: pytest.CaptureFixture[str]):
    logger = logging.getLogger(_LOGGER_NAME)

    with config.patch(database={"dialect": "memory", "echo": True}):
        start_engine()

    assert isinstance(logger.handlers[0], _SqlHandler)
    assert logger.parent and logger.parent.level == logging.INFO
    assert (out := capsys.readouterr()).out and not out.err


def test_clearing_sqlite(tmp_path: pathlib.Path):
    path = tmp_path.joinpath(secrets.token_hex())
    assert not path.exists()

    path.write_bytes(secrets.token_bytes())

    stat = path.stat()
    assert stat.st_size != 0

    database = {"dialect": "sqlite", "path": path, "clear": True}

    with config.patch(database=database):
        engine = start_engine()
        assert engine.url.database in (path, str(path))

    assert stat.st_ctime_ns < path.stat().st_ctime_ns
