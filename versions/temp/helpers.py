import os

import requests
from dotenv import load_dotenv

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

async def get_summoner_info(summoner_name: str, region: str) -> dict:
    """
    Get summoner by name

    Args:
        summoner_name (str): Summoner name
        region (str): Region

    Returns:
        dict: Summoner data
    """
    url = f"https://{region}.{RIOT_API_BASE_URL}{RIOT_API_ROUTES['summoner'].format(summonerName=summoner_name)}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

async def get_match_ids_by_puuid(puuid: str, region: str) -> list:
    """
    Get match ids by puuid

    Args:
        puuid (str): Puuid
        region (str): Region

    Returns:
        list: Match ids
    """
    url = f"https://{region}.{RIOT_API_BASE_URL}{RIOT_API_ROUTES['match_by_puuid'].format(puuid=puuid)}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

async def get_match_by_id(match_id: str, region: str) -> dict:
    """
    Get match by id

    Args:
        match_id (str): Match id
        region (str): Region

    Returns:
        dict: Match data
    """
    url = f"https://{region}.{RIOT_API_BASE_URL}{RIOT_API_ROUTES['match_by_id'].format(matchId=match_id)}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

async def get_match_timeline_by_id(match_id: str, region: str) -> dict:
    """
    Get match timeline by id

    Args:
        match_id (str): Match id
        region (str): Region

    Returns:
        dict: Match timeline data
    """
    url = f"https://{region}.{RIOT_API_BASE_URL}{RIOT_API_ROUTES['match_timeline'].format(matchId=match_id)}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()
