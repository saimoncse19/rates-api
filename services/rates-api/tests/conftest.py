import pytest
from starlette.testclient import TestClient
import databases
import sqlalchemy

from src.main import app

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


@pytest.fixture(scope="module")
def mock_app():
    with TestClient(app) as client:
        yield client
