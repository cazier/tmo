import typing

from fastapi.testclient import TestClient

from tmo.web import api_router


def test_months(database: dict[str, typing.Any]):
    assert True


import json
import pathlib

pathlib.Path("tests", "database.json").write_text(json.dumps(database, indent=4, sort_keys=True))
