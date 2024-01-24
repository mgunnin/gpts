import os

from fastapi import APIRouter
from riotwatcher import ApiError, LolWatcher

watcher_router = APIRouter()

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
QUEUE_TYPE_ROUTES = {"ranked": "ranked", "normal": "normal", "tourney": "tourney"}

lol_watcher = LolWatcher('RGAPI-de85bb37-76e5-6890-9a94-fcf7b1bf14a6')


@watcher_router.get("/lol_watcher/summoner/{summoner_name}")
async def summoner_info(summoner_name: str, region: str = "na1"):
    summoner = lol_watcher.summoner.by_name(region, summoner_name)
    return summoner


@watcher_router.get("/lol_watcher/match_history/<puuid>")
async def match_history(puuid, region: str = "na1"):
    matches = lol_watcher.match.matchlist_by_puuid(region, puuid, queue=420)
    return matches


@watcher_router.get("/lol_watcher/match_details/{match_id}")
async def get_match_details(match_id: str, region: str = "na1"):
    try:
        return lol_watcher.match.by_id(region, match_id)
    except ApiError:
        return {"error": "Unable to retrieve match details"}


@watcher_router.get("/lol_watcher/participants_data/{match_id}")
async def get_participant_data(match_id: str, region: str = "na1"):
    match = lol_watcher.match.by_id(region, match_id).json()

    participants = match["info"]["participants"]

    participants_data = []
    for participant in participants:
        participant_data = {
            "summonerName": participant["summonerName"],
            "championName": participant["championName"],
            "kills": participant["kills"],
            "deaths": participant["deaths"],
            "assists": participant["assists"],
            "win": participant["win"],
        }
        participants_data.append(participant_data)

    return participants_data





@watcher_router.get("/lol_watcher/team_data/{match_id}/{team_side}")
async def get_team_data(match_id: str, team_side: str, region: str = "na1"):
    match = lol_watcher.match.by_id(region, match_id).json()

    participants = match["info"]["participants"]
    blue_team = [p for p in participants if p["teamId"] == 100]
    red_team = [p for p in participants if p["teamId"] == 200]

    team = blue_team if team_side.lower() == "blue" else red_team
    team_id = 100 if team_side.lower() == "blue" else 200

    team_data = {
        "win": any(p["win"] for p in team),
        "first_blood": match["info"]["teams"][str(team_id)]["objectives"][
            "championKills"
        ]
        == 1,
        "first_tower": match["info"]["teams"][str(team_id)]["objectives"]["towerKills"]
        == 1,
        "tower_kills": match["info"]["teams"][str(team_id)]["objectives"]["towerKills"],
        "inhibitor_kills": match["info"]["teams"][str(team_id)]["objectives"][
            "inhibitorKills"
        ],
        "baron_kills": match["info"]["teams"][str(team_id)]["objectives"]["baronKills"],
        "dragon_kills": match["info"]["teams"][str(team_id)]["objectives"][
            "dragonKills"
        ],
        "rift_herald_kills": match["info"]["teams"][str(team_id)]["objectives"][
            "riftHeraldKills"
        ],
    }

    return team_data


@watcher_router.get("/lol_watcher/player_data/{match_id}/{name}")
async def find_player_data(match_id: str, name: str, region: str = "na1"):
    match = await lol_watcher.match.by_id(region, match_id).json()
    for participant in match["info"]["participants"]:
        if participant["summonerName"] == name:
            return {
                "championName": participant["championName"],
                "champLevel": participant["champLevel"],
                "kills": participant["kills"],
                "deaths": participant["deaths"],
                "assists": participant["assists"],
                "win": participant["win"],
            }
            
