import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List
import httpx
import uvicorn

# Initialize FastAPI app
app = FastAPI()

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
OPENAPI_API_URL = os.getenv("OPENAPI_API_URL")
RIOT_API_BASE_URL = "api.riotgames.com"
REGIONS = ["na1", "br1", "eun1", "euw1", "jp1", "kr"]
MASS_REGIONS = ["americas", "europe", "asia", "sea"]
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
      raise HTTPException(status_code=response.status_code,
                          detail=response.text)
    return response.json()


# FastAPI route to get summoner info using summoner name
@app.get("/summoner/{summoner_name}")
async def get_summoner_info(summoner_name: str, region: str = "na1"):
  if region not in REGIONS:
    raise HTTPException(status_code=400, detail="Invalid region")

  region_to_mass_region = {
      "na1": "americas",
      "br1": "americas",
      "eun1": "europe",
      "euw1": "europe",
      "jp1": "asia",
      "kr": "asia",
      "oc1": "sea"
  }
  if region is None:
    region = "na1"
  mass_region = region_to_mass_region.get(region, "americas")

  route = RIOT_API_ROUTES["summoner"].format(summonerName=summoner_name)
  RIOT_API_URL = f"https://{region}.{RIOT_API_BASE_URL}{route}"
  headers = {"X-Riot-Token": RIOT_API_KEY}
  response = await get_api_response(RIOT_API_URL, headers)
  if response.get('status_code') == 200:
    response = response.get('json')
  return {
      "summoner_name": summoner_name,
      "region": region,
      "mass_region": mass_region,
      "puuid": response.get("puuid")
  }


# FastAPI route to get match IDs using puuid
@app.get("/matches/by-puuid/{puuid}")
async def get_match_ids(puuid: str, mass_region: str, no_games: int):
  if mass_region not in MASS_REGIONS:
    raise HTTPException(status_code=400, detail="Invalid mass region")

  route = RIOT_API_ROUTES["match_by_puuid"].format(puuid=puuid)
  RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
  headers = {"X-Riot-Token": RIOT_API_KEY}
  match_ids = await get_api_response(RIOT_API_URL, headers)

  # Return only the number of games requested
  return match_ids[:no_games]


# FastAPI route to get match data using match ID
@app.get("/match_data/{match_id}")
async def get_match_data(match_id: str, mass_region: str):
  route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
  RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
  headers = {"X-Riot-Token": RIOT_API_KEY}
  return await get_api_response(RIOT_API_URL, headers)


# Gather all data
@app.get("/player_data/{match_id}/{puuid}")
async def find_player_data(match_id: str, puuid: str, mass_region: str):
  route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
  RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
  headers = {"X-Riot-Token": RIOT_API_KEY}
  match_data = await get_api_response(RIOT_API_URL, headers)
  participants = match_data['metadata']['participants']
  player_index = participants.index(puuid)
  player_data = match_data['info']['participants'][player_index]
  return player_data


@app.get("/gather_all_data/{puuid}/{no_games}")
async def gather_all_data(puuid: str, no_games: int, mass_region: str):
  # Get match_ids for the number of games requested
  match_ids = await get_match_ids(puuid, mass_region, no_games)

  # We initialise an empty dictionary to store data for each game
  data = {'champion': [], 'kills': [], 'deaths': [], 'assists': [], 'win': []}

  for match_id in match_ids:
    # run the two functions to get the player data from the match ID
    await get_match_data(match_id, mass_region)
    player_data = await find_player_data(match_id, puuid, mass_region)

    # assign the variables we're interested in
    champion = player_data['championName']
    k = player_data['kills']
    d = player_data['deaths']
    a = player_data['assists']
    win = player_data['win']

    # add them to our dataset
    data['champion'].append(champion)
    data['kills'].append(k)
    data['deaths'].append(d)
    data['assists'].append(a)
    data['win'].append(win)

  return data


# Analyze the gathered data
def analyze_player_data(data):
  # Initialize variables to store total stats
  total_kills = 0
  total_deaths = 0
  total_assists = 0
  total_wins = 0

  # Calculate total stats
  for match_data in data:
    total_kills += match_data['kills']
    total_deaths += match_data['deaths']
    total_assists += match_data['assists']
    total_wins += match_data['win']

  # Calculate averages
  average_kills = total_kills / len(data)
  average_deaths = total_deaths / len(data)
  average_assists = total_assists / len(data)
  win_rate = total_wins / len(data)

  # Return analysis results
  return {
      'average_kills': average_kills,
      'average_deaths': average_deaths,
      'average_assists': average_assists,
      'win_rate': win_rate,
  }


async def master_function(summoner_name: str, region: str, no_games: int):
  # Get puuid for the summoner name
  summoner_info = await get_summoner_info(summoner_name, region)
  puuid = summoner_info['id']

  # Get match_ids for the last no_games games
  match_ids = await get_match_ids(puuid, region, no_games)

  # Gather data for each match
  data = await gather_all_data(puuid, match_ids, region)

  # Analyze the gathered data
  analysis_results = analyze_player_data(data)

  return analysis_results


class PlayerStats(BaseModel):
  assists: int
  deaths: int
  kills: int
  goldPerMinute: float
  damagePerMinute: float
  killParticipation: float
  totalHeal: int
  totalDamageDealtToChampions: int
  visionScore: int


class Match(BaseModel):
  gameId: int
  platformId: str
  gameCreation: int
  gameDuration: int
  queueId: int
  mapId: int
  seasonId: int
  gameVersion: str
  gameMode: str
  gameType: str
  teams: List[dict]
  participants: List[PlayerStats]
  participantIdentities: List[dict]


class SummonerData(BaseModel):
  matches: List[Match]


@app.post("/analyze_match_data")
def analyze_match_history(summoner_data: SummonerData):
  if not summoner_data.matches:
    return {"error": "No match data available"}

  total_matches = len(summoner_data.matches)
  total_kills = 0
  total_deaths = 0
  total_assists = 0
  total_gold_per_minute = 0
  total_damage_per_minute = 0
  total_kill_participation = 0
  total_heal = 0
  total_damage_dealt_to_champions = 0
  total_vision_score = 0

  for match in summoner_data.matches:
    for participant in match.participants:
      total_kills += participant.kills
      total_deaths += participant.deaths
      total_assists += participant.assists
      total_gold_per_minute += participant.goldPerMinute
      total_damage_per_minute += participant.damagePerMinute
      total_kill_participation += participant.killParticipation
      total_heal += participant.totalHeal
      total_damage_dealt_to_champions += participant.totalDamageDealtToChampions
      total_vision_score += participant.visionScore

  average_kills = total_kills / total_matches
  average_deaths = total_deaths / total_matches
  average_assists = total_assists / total_matches
  average_gold_per_minute = total_gold_per_minute / total_matches
  average_damage_per_minute = total_damage_per_minute / total_matches
  average_kill_participation = total_kill_participation / total_matches
  average_heal = total_heal / total_matches
  average_damage_dealt_to_champions = total_damage_dealt_to_champions / total_matches
  average_vision_score = total_vision_score / total_matches

  return {
      "totalMatches": total_matches,
      "averageKills": average_kills,
      "averageDeaths": average_deaths,
      "averageAssists": average_assists,
      "averageGoldPerMinute": average_gold_per_minute,
      "averageDamagePerMinute": average_damage_per_minute,
      "averageKillParticipation": average_kill_participation,
      "averageHeal": average_heal,
      "averageDamageDealtToChampions": average_damage_dealt_to_champions,
      "averageVisionScore": average_vision_score,
  }


@app.get("/")
def home():
  return {"message": "Welcome to the Esports Playmaker"}


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
