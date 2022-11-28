import datetime
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from databases.core import Record

from .db import database

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

app = FastAPI()


class InvalidDateRangeException(HTTPException):
    """Raise when start date is greater than end date."""


async def get_codes_from_slugs(slugs: list[str]) -> list[Record]:
    """
    Retrieve port codes based on a list of region slugs
    :param slugs: a list of region slugs
    :type slugs: list[str]
    :return: a list of db records
    :rtype: list[Record]
    """
    ports = await database.fetch_all(f"SELECT code, name FROM ports "
                                     f"WHERE parent_slug IN"
                                     f"('{get_query_compatible_list(slugs)}')")
    return ports


async def slug_to_codes(slug: str) -> list[str]:
    """
    Retrieve all the port codes for a given slug that represents a geographic region

    :param slug: A region slug ex: north_europe_main
    :type slug: str
    :return: A list of port codes for a given region slug
    :rtype: list[str]
    """
    regions = await database.fetch_all(f"SELECT slug from regions where slug='{slug}'"
                                       f" and parent_slug IS NULL")
    root_regions = jsonable_encoder(regions)
    if not root_regions:
        ports = await get_codes_from_slugs([slug])
    else:
        slug_of_root = root_regions[0].get("slug")
        all_regions = await database.fetch_all(f"SELECT slug from regions where "
                                               f"parent_slug='{slug_of_root}'")
        ports = await get_codes_from_slugs([region.slug for region in all_regions])
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
    Retrieve average prices for each day on a route between origin and
    destination for the given date range

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
    :raise InvalidDateRangeException: when date_to predates date_from
    """
    if date_from > date_to:
        error_message = "Invalid date range, start date is greater than end date."
        LOGGER.error(error_message)
        raise InvalidDateRangeException(status_code=400, detail=error_message)

    origins = [origin] if origin == origin.upper() else \
        await slug_to_codes(origin)
    destinations = [destination] if destination == destination.upper() else \
        await slug_to_codes(destination)

    query = f"""SELECT day, (CASE WHEN COUNT(*) > 2 THEN avg(price)
    ELSE null END) as average_price
    FROM prices WHERE orig_code IN ('{get_query_compatible_list(origins)}')
    and dest_code IN ('{get_query_compatible_list(destinations)}')
    and day BETWEEN '{date_from}' and  '{date_to}' GROUP BY day ORDER BY day
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
