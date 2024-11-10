from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data_population_script import (
    populate_champion_mastery,
    populate_league_info,
    populate_match_data,
    populate_summoner_data,
)
from database import Database
from models import ChampionMastery, LeagueInfo, MatchData, Summoner
from riot_api_wrapper import RiotAPIWrapper

app = FastAPI()

# Setup CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RiotAPIWrapper and Database instances
api_wrapper = RiotAPIWrapper()
db = Database()


@app.on_event("startup")
async def startup_event():
    # Connect to the database
    db.connect()
    # Create tables if they don't exist
    db.create_tables()
    # Populate the database with initial data
    for region in ["na1"]:
        populate_summoner_data(api_wrapper, db, region)
        populate_champion_mastery(api_wrapper, db, region)
        populate_league_info(api_wrapper, db, region)
        populate_match_data(api_wrapper, db, region)


@app.get("/summoner/{region}/{summoner_name}", response_model=Summoner)
async def get_summoner(region: str, summoner_name: str):
    summoner_info = api_wrapper.get_summoner_by_name(region, summoner_name)
    if summoner_info:
        return Summoner(**summoner_info)
    else:
        raise HTTPException(status_code=404, detail="Summoner not found")


@app.get(
    "/champion-mastery/{region}/{summoner_id}", response_model=List[ChampionMastery]
)
async def get_champion_mastery(region: str, summoner_id: str):
    mastery_info = api_wrapper.get_champion_mastery(region, summoner_id)
    if mastery_info:
        return [ChampionMastery(**mastery) for mastery in mastery_info]
    else:
        raise HTTPException(
            status_code=404, detail="Champion mastery information not found"
        )


@app.get("/league-info/{region}/{summoner_id}", response_model=List[LeagueInfo])
async def get_league_info(region: str, summoner_id: str):
    league_info = api_wrapper.get_league_info(region, summoner_id)
    if league_info:
        return [LeagueInfo(**league) for league in league_info]
    else:
        raise HTTPException(status_code=404, detail="League information not found")


# Additional endpoints for match data and player performance can be added here following the same pattern

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
