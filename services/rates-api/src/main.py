from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home():
    """The entrypoint of our Rates API"""
    return {"message": "Welcome! from Rates API."}
