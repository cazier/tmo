# mypy: disable-error-code="no-untyped-def"

import tmo.dependencies
from tmo import config


def test_initialization():
    assert tmo.dependencies.engine is None
    database = {"dialect": "memory"}

    with config.patch(database=database):
        engine = next(tmo.dependencies.get_session())

    assert engine is not None
