import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse

from models import MassRegion, SummonerData
from utils import get_api_response

load_dotenv()

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
    """
    This endpoint retrieves the summoner information for a given summoner name and region.

    Parameters:
    summoner_name (str): The name of the summoner.
    region (str, optional): The region where the summoner is located. Defaults to "na1".

    Returns:
    dict: A dictionary containing the summoner name, region, mass region, and puuid.
    """
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

# Route to get match IDs using puuid
@router.get("/matches/by-puuid/{puuid}")
async def get_match_ids(puuid: str, no_games: int, mass_region: MassRegion = MassRegion.americas):

    """
    This endpoint retrieves the match IDs for a given puuid and mass region.

    Parameters:
    puuid (str): The puuid of the summoner.
    no_games (int): The number of games to retrieve.
    mass_region (MassRegion, optional): The mass region where the summoner is located. Defaults to MassRegion.americas.

    Returns:
    list: A list containing the match IDs.
    """
    route = RIOT_API_ROUTES["match_by_puuid"].format(puuid=puuid)
    RIOT_API_URL = f"https://{mass_region.value}.{RIOT_API_BASE_URL}{route}?start=0&count={no_games}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    match_ids = await get_api_response(RIOT_API_URL, headers)

    return match_ids


# Route to get match data using match ID
@router.get("/match_data/{match_id}")
async def get_match_data(match_id: str, mass_region: MassRegion = MassRegion.americas):
    """
    This endpoint retrieves the match data for a given match ID and mass region.

    Parameters:
    match_id (str): The match ID of the game.
    mass_region (MassRegion, optional): The mass region where the game was played. Defaults to MassRegion.americas.

    Returns:
    dict: A dictionary containing the match data.
    """
    route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
    RIOT_API_URL = f"https://{mass_region.value}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    return await get_api_response(RIOT_API_URL, headers)

# Gather all data
@router.get("/player_data/{match_id}/{puuid}")
async def find_player_data(match_id: str, puuid: str, mass_region: MassRegion = MassRegion.americas):
    """
    This endpoint retrieves the player data for a given match ID, puuid and mass region.

    Parameters:
    match_id (str): The match ID of the game.
    puuid (str): The puuid of the summoner.
    mass_region (MassRegion, optional): The mass region where the game was played. Defaults to MassRegion.americas.

    Returns:
    dict: A dictionary containing the player data.
    """
    route = RIOT_API_ROUTES["match_by_id"].format(matchId=match_id)
    RIOT_API_URL = f"https://{mass_region.value}.{RIOT_API_BASE_URL}{route}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    match_data = await get_api_response(RIOT_API_URL, headers)
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]
    return player_data

@router.get("/gather_all_data/{puuid}/{no_games}")
async def gather_all_data(puuid: str, no_games: int, mass_region: MassRegion = MassRegion.americas):
    """
    This endpoint retrieves all the data for a given puuid and number of games in a specific mass region.

    Parameters:
    puuid (str): The puuid of the summoner.
    no_games (int): The number of games to retrieve data for.
    mass_region (MassRegion, optional): The mass region where the games were played. Defaults to MassRegion.americas.

    Returns:
    dict: A dictionary containing the data for each game.
    """
    # Get match_ids for the number of games requested
    match_ids = await get_match_ids(puuid, no_games, mass_region)

    # We initialise an empty dictionary to store data for each game
    data = {
        'champion': [],
        'champLevel': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': [],
        'teamposition': [],
        'role': [],
        'timeplayed': [],
        'totaldamagedealt': [],
        'goldearned': [],
        'goldspent': []
    }

    for match_id in match_ids:
        # run the two functions to get the player data from the match ID
        await get_match_data(match_id, mass_region)
        player_data = await find_player_data(match_id, puuid, mass_region)

        # Core Stats Variables
        champion = player_data['championName']
        champLevel = player_data['champLevel']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        win = player_data['win']

        #Secondary Stats Variables
        teamPosition = player_data['teamPosition']
        role = player_data['role']
        timePlayed = player_data['timePlayed'] / 60
        totalDamageDealt = player_data['totalDamageDealt']
        goldEarned = player_data['goldEarned']
        goldSpent = player_data['goldSpent']

        # Core Stats
        data['champion'].append(champion)
        data['champLevel'].append(champLevel)
        data['kills'].append(k)
        data['deaths'].append(d)
        data['assists'].append(a)
        data['win'].append(win)

        # Secondary Stats
        data['teamposition'].append(teamPosition)
        data['role'].append(role)
        data['timeplayed'].append(timePlayed)
        data['totaldamagedealt'].append(totalDamageDealt)
        data['goldearned'].append(goldEarned)
        data['goldspent'].append(goldSpent)


    return data

# Analyze the gathered data
@router.get("/analyze_player_data/{data}")
async def analyze_player_data(data):
    """
    This endpoint analyzes the data for a given summoner.

    Parameters:
    data (dict): The data to analyze.

    Returns:
    dict: A dictionary containing the analysis results.
    """
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

@router.post("/analyze_match_data")
async def analyze_match_history(summoner_data: SummonerData):
    """
    This endpoint analyzes the match history for a given summoner.

    Parameters:
    summoner_data (SummonerData): The data of the summoner whose match history is to be analyzed.

    Returns:
    dict: A dictionary containing the analysis results.
    """
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
    total_gold_earned = sum(participant.gold_earned for match in summoner_data.matches for participant in match.participants)
    total_gold_spent = sum(participant.gold_spent for match in summoner_data.matches for participant in match.participants)

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
        "average_gold_earned": total_gold_earned / total_matches,
        "average_gold_spent": total_gold_spent / total_matches,
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
