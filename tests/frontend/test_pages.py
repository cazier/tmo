# mypy: disable-error-code="no-untyped-def"
import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.usefixtures("insert_into_database")]


def test_errors(client: TestClient):
    response = client.get("/missing")
    assert response.status_code == 404
