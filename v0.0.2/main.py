import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from routes import analysis_routes
from typing import List, Optional
import httpx
import uvicorn

# Initialize FastAPI app
app = FastAPI()

app.include_router(analysis_routes.router)

# Set up CORS middleware
origins = [
    "http://localhost:8000",
    "https://lacra-gpt-lol.replit.app/",
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY environment variable is not set")

# Constants
RIOT_API_BASE_URL = "api.riotgames.com"
REGIONS = ["na1", "eun1", "euw1", "jp1", "kr", "br1"]
MASS_REGIONS = ["americas", "europe", "sea"]
RIOT_API_ROUTES = {
    "summoner": "/lol/summoner/v4/summoners/by-name/{summonerName}",
    "match_by_puuid": "/lol/match/v5/matches/by-puuid/{puuid}/ids",
    "match_by_id": "/lol/match/v5/matches/{matchId}",
    "match_timeline": "/lol/match/v5/matches/{matchId}/timeline",
}
QUEUE_ID_ROUTES = {
    "draft_pick": 400,
    "ranked_solo": 420,
    "blind_pick": 430,
    "ranked_flex": 440,
    "aram": 450,
}
QUEUE_TYPE_ROUTES = {
    "ranked": "ranked",
    "normal": "normal",
    "tourney": "tourney"
}

# Helper function to get API response
async def get_api_response(url: str, headers: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()


# FastAPI route to accept user's summoner name and region as query parameters
@app.get("/user_input")
async def user_input(summoner_name: str, region: Optional[str] = "na1"):
    region_to_mass_region = {
        "na1": "americas",
        "br1": "americas",
        "eun1": "europe",
        "euw1": "europe",
        "jp1": "sea",
        "kr": "sea",
    }
    if region is None:
        region = "na1"
    mass_region = region_to_mass_region.get(region, "americas")
    return {
        "summoner_name": summoner_name,
        "region": region,
        "mass_region": mass_region,
    }


# FastAPI route to get summoner's puuid
@app.get("/summoner/{summoner_name}")
async def get_summoner_info(summoner_name: str, region: str = "na1"):
    if region not in REGIONS:
        raise HTTPException(status_code=400, detail="Invalid region")

    route = RIOT_API_ROUTES["summoner"].format(summonerName=summoner_name)
    RIOT_API_URL = f"https://{region}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    return await get_api_response(RIOT_API_URL, headers)


# FastAPI route to get match IDs using puuid
@app.get("/matches/by-puuid/{puuid}")
async def get_match_ids(puuid: str, mass_region: str):
    if mass_region not in MASS_REGIONS:
        raise HTTPException(status_code=400, detail="Invalid mass region")

    route = RIOT_API_ROUTES["match_by_puuid"].format(puuid=puuid)
    RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    return await get_api_response(RIOT_API_URL, headers)


# FastAPI route to get match data using match ID
@app.get("/match_data/{match_id}")
async def get_match_data(match_id: str, mass_region: str):
    route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
    RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    return await get_api_response(RIOT_API_URL, headers)


templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/logo.png")
async def plugin_logo():
    return FileResponse("logo.png", media_type="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("ai-plugin.json", "r") as f:
        json_content = f.read()
    return Response(content=json_content, media_type="application/json")


@app.get("/openapi.yaml")
async def openapi_spec(request: Request):
    host = request.client.host if request.client else "localhost"
    with open("openapi.yaml", "r") as f:
        yaml_content = f.read()
    yaml_content = yaml_content.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return Response(content=yaml_content, media_type="application/yaml")


# Run the async function using the event loop
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
