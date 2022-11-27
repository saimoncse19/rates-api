import datetime
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

from .db import database

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

app = FastAPI()


class InvalidDateRangeException(HTTPException):
    """Raise when start date is greater than end date."""


async def ports_slug_to_code(slug: str) -> list[str]:
    """
    Retrieve all the port codes for a given slug that represents a geographic region

    :param slug: A region slug ex: north_europe_main
    :type slug: str
    :return: A list of port codes for a given region slug
    :rtype: list[str]
    """
    ports = await database.fetch_all(f"SELECT code FROM ports WHERE parent_slug='{slug}'")
    return [port.code for port in ports]


def get_query_compatible_list(data: list) -> str:
    """
    Produce a string representation of a Postgres list to use in query from a Python list

    :param data: a list of data
    :type data: list
    :return: a query compatible string representing a postgres list
    :rtype: str
    """
    sub_query = "', '".join(data)
    return sub_query


@app.get("/")
async def home():
    """The entrypoint of our Rates API"""
    return {"message": "Welcome! from Rates API."}


@app.get("/rates")
async def average_rates(date_from: datetime.date,
                        date_to: datetime.date,
                        origin: str,
                        destination: str) -> JSONResponse:
    """
    Retrieve average prices for each day on a route between origin and destination for the given date range

    :param date_from: the start date
    :type date_from: datetime.date
    :param date_to: the end date
    :type date_to: datetime.date
    :param origin: port code or region slug
    :type origin: str
    :param destination: port code or region slug
    :type destination: str
    :return: average prices between origin to destination for each day
    :rtype: JSONResponse
    :raise MissingDateException: when an expected date is missing
    :raise InvalidDateRangeException: when date_to predates date_from
    :raise MissingCodeOrSlugException: when port code or slug is missing
    """
    if date_from > date_to:
        error_message = "Invalid date range, start date is greater than end date."
        LOGGER.error(error_message)
        raise InvalidDateRangeException(status_code=400, detail=error_message)

    origins = [origin] if origin == origin.upper() else \
        await ports_slug_to_code(origin)
    destinations = [destination] if destination == destination.upper() else \
        await ports_slug_to_code(destination)

    query = f"""SELECT day, (CASE WHEN COUNT(*) > 2 THEN avg(price) ELSE null END) as average_price 
    FROM prices WHERE orig_code IN ('{get_query_compatible_list(origins)}')
    and dest_code IN ('{get_query_compatible_list(destinations)}')
    and day BETWEEN '{date_from}' and  '{date_to}' GROUP BY day
    """

    average_prices_objs = await database.fetch_all(query)
    average_prices = jsonable_encoder(average_prices_objs)
    return JSONResponse(content=average_prices)


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
