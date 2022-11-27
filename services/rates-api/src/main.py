from fastapi import FastAPI

from .db import database

app = FastAPI()


@app.get("/")
async def home():
    """The entrypoint of our Rates API"""
    return {"message": "Welcome! from Rates API."}


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
