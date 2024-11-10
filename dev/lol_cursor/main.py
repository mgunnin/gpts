import os
import traceback
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from authentication_handler import authenticate_user
from dashboard_handler import generate_dashboard
from data_population import (fetch_top_players, populate_champion_mastery,
                             populate_league_info, populate_summoner_data)
from database.database import Base, Summoner, get_db
from match_data import MatchDataHandler
from riot_api_wrapper import RiotAPIWrapper
from scheduler_handler import start_background_tasks

DATABASE_URL = "postgresql+asyncpg://postgres:gl94hhp89k2YpcVx@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL)

app = FastAPI()

app.mount("/dashboard", StaticFiles(directory="dashboard"), name="dashboard")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("RIOT_API_KEY")

# Initialize Riot API Wrapper with your API key
if API_KEY is None:
    raise ValueError("API key is required")
riot_api = RiotAPIWrapper(api_key=API_KEY)


@app.on_event("startup")
async def startup():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.post("/login/")
async def login(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"message": "User authenticated successfully"}


@app.get("/dashboard/{region}/{summoner_name}")
async def get_summoner_dashboard(region: str, summoner_name: str) -> Any:
    """
    Get the dashboard for a specific summoner in a given region.

    Args:
        region (str): The region of the summoner.
        summoner_name (str): The name of the summoner.

    Returns:
        Any: The generated dashboard data.
    """
    try:
        data = generate_dashboard(riot_api, region, summoner_name)
        return data
    except Exception as e:
        return {"error": str(e)}


@app.get("/summoner/{region}/{summoner_name}")
async def get_summoner_data(region: str, summoner_name: str):
    try:
        await populate_summoner_data(riot_api, region, summoner_name)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "message": f"Summoner data for {summoner_name} in {region} populated successfully"
    }


@app.get("/populate/matches/{region}/{puuid}/")
async def populate_match_data(puuid: str, region: str = "na1"):
    try:
        # Get the summoner's PUUID from the database
        async with get_db() as session:
            result = session.execute(select(Summoner).filter_by(puuid=puuid))
            summoner = result.scalars().first()
            if not summoner:
                raise HTTPException(status_code=404, detail="Summoner not found")

        await MatchDataHandler.fetch_match_data(puuid, region)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Match data populated successfully"}


@app.get("/populate/champion-mastery/{region}/{puuid}/")
async def populate_champion_mastery_data(puuid: str, region: str = "na1"):
    try:
        # Get the summoner's PUUID from the database
        async with get_db() as session:
            result = session.execute(
                select(Summoner).filter_by(puuid=puuid, region=region)
            )
            summoner = result.scalars().first()
            if not summoner:
                raise HTTPException(status_code=404, detail="Summoner not found")
        await populate_champion_mastery(riot_api, region, puuid)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Champion mastery data populated successfully"}


@app.get("/populate/league-info/{region}/{summoner_name}/")
async def populate_league_info_data(region: str, summoner_name: str):
    try:
        await populate_league_info(riot_api, region, summoner_name)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "League info data populated successfully"}


@app.get("/update/top-players")
async def update_data(region: str):
    try:
        await fetch_top_players(riot_api, region=region)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Data updated successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
