import pytest
from starlette.testclient import TestClient

from src.main import app


@pytest.fixture(scope="module")
def mock_app():
    client = TestClient(app)
    yield client
