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


@pytest.fixture
def mock_rate_response():

    mock_response = [
        {
          "day": "2016-01-01",
          "average_price": 1310.2200886262924
        },
        {
          "day": "2016-01-02",
          "average_price": 1310.1875923190546
        },
        {
          "day": "2016-01-05",
          "average_price": 1312.2635658914728
        },
        {
          "day": "2016-01-06",
          "average_price": 1309.2899224806201
        },
        {
          "day": "2016-01-07",
          "average_price": 1312.2635658914728
        },
        {
          "day": "2016-01-08",
          "average_price": 1311.843410852713
        },
        {
          "day": "2016-01-09",
          "average_price": 1330.838124054463
        },
        {
          "day": "2016-01-10",
          "average_price": 1332.2537764350452
        }
    ]

    return mock_response


@pytest.fixture(scope="module")
def mock_app():
    with TestClient(app) as client:
        yield client

