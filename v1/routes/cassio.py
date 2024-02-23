import os

import cassiopeia as cass
from dotenv import load_dotenv
from fastapi import APIRouter

from v1.models import MassRegion, SummonerData

load_dotenv()

cass_router = APIRouter()

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


@cass_router.get("/cass/summoner/{summoner_name}")
async def get_summoner_info(summoner_name: str, region: str = "NA"):
    """
    Get summoner info using Cassiopeia

    Parameters:
    summoner_name (str): The name of the summoner to lookup
    region (str, optional): The region to lookup the summoner in. Defaults to "NA".

    Returns:
    dict: A dictionary containing the summoner info
    """
    summoner = cass.get_summoner(name=summoner_name, region=region)
    return summoner.to_dict()


@cass_router.get("/cass/match_ids/{summoner_name}")
async def get_match_ids(summoner_name: str, region: str = "NA"):
    """
    Retrieve match ids for a summoner using the Cassiopeia API Wrapper

    Parameters:
    - summoner_name (str): The name of the summoner
    - no_games (int): The number of match ids to retrieve
    - region (str, optional): The region of the summoner. Defaults to "NA".

    Returns:
    - list[int]: A list containing the match ids for the summoner
    """

    # Get the summoner object
    summoner = cass.get_summoner(name=summoner_name, region=region)

    # Retrieve the match history
    match_history = summoner.match_history

    # Extract just the match ids
    match_ids = [match.id for match in match_history]

    return match_ids


@cass_router.get("/cass/match_details/{match_id}")
async def get_match_details(match_id: int, region: str = "NA"):
    """
    Retrieve match details for a given match ID and region.

    Args:
        match_id (int): The ID of the match.
        region (str, optional): The region of the match. Defaults to "NA".

    Returns:
        dict: A dictionary containing match details.
    """
    match = cass.get_match(id=match_id, region=region)
    return match.to_dict()


@cass_router.get("/cass/participants_data/{match_id}")
async def get_participant_data(match_id: int, region: str = "NA"):
    match = cass.get_match(id=match_id, region=region)
    participants_data = []
    for participant in match.participants():
        participants_data.append(
            {
                "summoner": participant.summoner.name,
                "champion": participant.champion.name,
                "kills": participant.stats.kills,
                "deaths": participant.stats.deaths,
                "assists": participant.stats.assists,
                "win": participant.stats.win,
                "gold_earned": participant.stats.gold_earned,
                "total_damage_dealt_to_champions": participant.stats.total_damage_dealt_to_champions,
                "vision_score": participant.stats.vision_score,
                "turret_kills": participant.stats.turret_kills,
                "dragon_kills": participant.stats.dragon_kills,
                "baron_kills": participant.stats.baron_kills,
                "rift_herald_kills": participant.stats.rift_herald_kills,
                "minions_killed": participant.stats.total_minions_killed,
            }
        )
    return participants_data


@cass_router.get("/cass/team_data/{match_id}/{team_side}")
async def get_team_data(match_id: int, team_side: str):
    """
    Retrieve data for a specific team in a match.

    Parameters:
    - match_id (int): The ID of the match.
    - team_side (str): The side of the team ("blue" or "red").

    Returns:
    - dict: A dictionary containing various data about the team, including win status, first blood, tower kills, etc.
    """
    match = cass.get_match(id=match_id, region="NA")
    team = match.blue_team if team_side.lower() == "blue" else match.red_team

    team_data = {
        "win": team.win,
        "first_blood": team.first_blood,
        "first_tower": team.first_tower,
        "first_inhibitor": team.first_inhibitor,
        "first_baron": team.first_baron,
        "first_dragon": team.first_dragon,
        "first_rift_herald": team.first_rift_herald,
        "tower_kills": team.tower_kills,
        "inhibitor_kills": team.inhibitor_kills,
        "baron_kills": team.baron_kills,
        "dragon_kills": team.dragon_kills,
        "rift_herald_kills": team.rift_herald_kills,
        "bans": [champion.name for champion in team.bans],
    }
    return team_data


@cass_router.get("/cass/match_data/{match_id}")
async def get_match_data(match_id: int, mass_region: MassRegion = MassRegion.americas):
    match = cass.get_match(id=match_id, region=mass_region)
    return match


@cass_router.get("/cass/player_data/{match_id}/{name}")
async def find_player_data(
    match_id: int, name: str, mass_region: MassRegion = MassRegion.americas
):
    match = cass.get_match(id=match_id, region=mass_region)
    participant = match.participants.find(name=name)
    return {
        "championName": participant.champion.name,
        "champLevel": participant.stats.champ_level,
        "kills": participant.stats.kills,
        "deaths": participant.stats.deaths,
        "assists": participant.stats.assists,
        "win": participant.team.win,
    }


@cass_router.get("/cass/gather_all_data/{name}/{no_games}")
async def gather_all_data(name: str, region: str = "NA"):
    # Get match_ids for the number of games requested
    match_ids = await get_match_ids(name, region)

    # We initialise an empty dictionary to store data for each game
    data = {
        "champion": [],
        "champLevel": [],
        "kills": [],
        "deaths": [],
        "assists": [],
        "win": [],
        "teamposition": [],
        "role": [],
        "timeplayed": [],
        "totaldamagedealt": [],
        "goldearned": [],
        "goldspent": [],
    }

    for match_id in match_ids:
        # Get match data using Cassiopeia
        match = cass.get_match(id=match_id, region=region)

        # Find player data using Cassiopeia
        participant = match.participants.find(name=name)

        # Core Stats Variables
        champion = participant.champion.name
        champLevel = participant.stats.champ_level
        k = participant.stats.kills
        d = participant.stats.deaths
        a = participant.stats.assists
        win = participant.team.win

        # Secondary Stats Variables
        teamPosition = participant.team.position
        role = participant.timeline.role
        timePlayed = participant.timeline.game_length_seconds / 60
        totalDamageDealt = participant.damage_stats.total_damage_dealt
        goldEarned = participant.stats.gold_earned
        goldSpent = participant.stats.gold_spent

        # Core Stats
        data["champion"].append(champion)
        data["champLevel"].append(champLevel)
        data["kills"].append(k)
        data["deaths"].append(d)
        data["assists"].append(a)
        data["win"].append(win)

        # Secondary Stats
        data["teamposition"].append(teamPosition)
        data["role"].append(role)
        data["timeplayed"].append(timePlayed)
        data["totaldamagedealt"].append(totalDamageDealt)
        data["goldearned"].append(goldEarned)
        data["goldspent"].append(goldSpent)

    return data


# Analyze the gathered data
@cass_router.get("/cass/analyze_player_data/{data}")
async def analyze_player_data(data):
    # Initialize variables to store total stats
    total_kills = 0
    total_deaths = 0
    total_assists = 0
    total_wins = 0

    # Calculate total stats
    for match_data in data:
        total_kills += match_data["kills"]
        total_deaths += match_data["deaths"]
        total_assists += match_data["assists"]
        total_wins += match_data["win"]

    # Calculate averages
    average_kills = total_kills / len(data)
    average_deaths = total_deaths / len(data)
    average_assists = total_assists / len(data)
    win_rate = total_wins / len(data)

    # Return analysis results
    return {
        "average_kills": average_kills,
        "average_deaths": average_deaths,
        "average_assists": average_assists,
        "win_rate": win_rate,
    }


@cass_router.post("/cass/analyze_match_data")
async def analyze_match_history(summoner_data: SummonerData):
    if not summoner_data.matches:
        return {"error": "No match data available"}

    total_matches = len(summoner_data.matches)
    total_kills = sum(
        participant.kills
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_deaths = sum(
        participant.deaths
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_assists = sum(
        participant.assists
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_gold_per_minute = sum(
        participant.gold_per_minute
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_damage_per_minute = sum(
        participant.damage_per_minute
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_kill_participation = sum(
        participant.kill_participation
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_heal = sum(
        participant.total_heal
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_damage_dealt_to_champions = sum(
        participant.total_damage_dealt_to_champions
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_vision_score = sum(
        participant.vision_score
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_gold_earned = sum(
        participant.gold_earned
        for match in summoner_data.matches
        for participant in match.participants
    )
    total_gold_spent = sum(
        participant.gold_spent
        for match in summoner_data.matches
        for participant in match.participants
    )

    return {
        "total_matches": total_matches,
        "average_kills": total_kills / total_matches,
        "average_deaths": total_deaths / total_matches,
        "average_assists": total_assists / total_matches,
        "average_gold_per_minute": total_gold_per_minute / total_matches,
        "average_damage_per_minute": total_damage_per_minute / total_matches,
        "average_kill_participation": total_kill_participation / total_matches,
        "average_heal": total_heal / total_matches,
        "average_damage_dealt_to_champions": total_damage_dealt_to_champions
        / total_matches,
        "average_vision_score": total_vision_score / total_matches,
        "average_gold_earned": total_gold_earned / total_matches,
        "average_gold_spent": total_gold_spent / total_matches,
    }
