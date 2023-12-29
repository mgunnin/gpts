import os

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse

from models import SummonerData
from utils import get_api_response

router = APIRouter()

# Constants
OPENAPI_API_URL = os.getenv("OPENAPI_API_URL")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
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

# Get summoner info using summoner name
@router.get("/summoner/{summoner_name}")
async def get_summoner_info(summoner_name: str, region: str = "na1"):
    RIOT_API_KEY = os.getenv("RIOT_API_KEY")
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
@router.get("/matches/by-puuid/{puuid}")
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
@router.get("/match_data/{match_id}")
async def get_match_data(match_id: str, mass_region: str):
    route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
    RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    return await get_api_response(RIOT_API_URL, headers)

# Gather all data
@router.get("/player_data/{match_id}/{puuid}")
async def find_player_data(match_id: str, puuid: str, mass_region: str):
    route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
    RIOT_API_URL = f"https://{mass_region}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    match_data = await get_api_response(RIOT_API_URL, headers)
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]
    return player_data

@router.get("/gather_all_data/{puuid}/{no_games}")
async def gather_all_data(puuid: str, no_games: int, mass_region: str):
    # Get match_ids for the number of games requested
    match_ids = await get_match_ids(puuid, mass_region, no_games)

    # We initialise an empty dictionary to store data for each game
    data = {
        'champion': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': []
    }

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
@router.get("/analyze_player_data/{data}")
async def analyze_player_data(data):
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

# FastAPI route to get all data
@router.get("/master_function/{summoner_name}/{mass_region}/{no_games}")
async def master_function(request: Request, mass_region: str, no_games: int):
    # Get puuid for the summoner name
    puuid = request.session.get("puuid")

    # Gather data for each match
    data = await gather_all_data(puuid, no_games, mass_region)

    # Analyze the gathered data
    analysis_results = await analyze_player_data(data)

    return analysis_results

@router.post("/analyze_match_data")
async def analyze_match_history(summoner_data: SummonerData):
    if not summoner_data.matches:
        return {"error": "No match data available"}

    total_matches = len(summoner_data.matches)
    total_kills = sum(participant.kills for match in summoner_data.matches for participant in match.participants)
    total_deaths = sum(participant.deaths for match in summoner_data.matches for participant in match.participants)
    total_assists = sum(participant.assists for match in summoner_data.matches for participant in match.participants)
    total_gold_per_minute = sum(participant.gold_per_minute for match in summoner_data.matches for participant in match.participants)
    total_damage_per_minute = sum(participant.damage_per_minute for match in summoner_data.matches for participant in match.participants)
    total_kill_participation = sum(participant.kill_participation for match in summoner_data.matches for participant in match.participants)
    total_heal = sum(participant.total_heal for match in summoner_data.matches for participant in match.participants)
    total_damage_dealt_to_champions = sum(participant.total_damage_dealt_to_champions for match in summoner_data.matches for participant in match.participants)
    total_vision_score = sum(participant.vision_score for match in summoner_data.matches for participant in match.participants)

    return {
        "total_matches": total_matches,
        "average_kills": total_kills / total_matches,
        "average_deaths": total_deaths / total_matches,
        "average_assists": total_assists / total_matches,
        "average_gold_per_minute": total_gold_per_minute / total_matches,
        "average_damage_per_minute": total_damage_per_minute / total_matches,
        "average_kill_participation": total_kill_participation / total_matches,
        "average_heal": total_heal / total_matches,
        "average_damage_dealt_to_champions": total_damage_dealt_to_champions / total_matches,
        "average_vision_score": total_vision_score / total_matches,
    }

@router.get("/")
async def home():
  return {"message": "Welcome to the Esports Playmaker"}

@router.get("/public/logo.png")
async def plugin_logo():
    return FileResponse("logo.png", media_type="image/png")


@router.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("ai-plugin.json", "r") as f:
        json_content = f.read()
    return Response(content=json_content, media_type="application/json")


@router.get("/openapi.yaml")
async def openapi_spec(request: Request):
    host = request.client.host if request.client else "localhost"
    with open("openapi.yaml", "r") as f:
        yaml_content = f.read()
    yaml_content = yaml_content.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return Response(content=yaml_content, media_type="application/yaml")
