# mypy: disable-error-code="no-untyped-def"

import tmo.web.dependencies
from tmo import config


def test_initialization():
    assert tmo.web.dependencies.engine is None
    database = {"dialect": "memory"}

    with config.patch(database=database):
        engine = next(tmo.web.dependencies.get_session())

    assert engine is not None
