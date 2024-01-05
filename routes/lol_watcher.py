import os

from dotenv import load_dotenv
from fastapi import APIRouter
from riotwatcher import LolWatcher

load_dotenv()

lol_watcher = LolWatcher('RGAPI-de85bb37-76e5-6890-9a94-fcf7b1bf14a6')
region = 'na1'
mass_region = 'americas'

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
QUEUE_TYPE_ROUTES = {
    "ranked": "ranked",
    "normal": "normal",
    "tourney": "tourney"
}

# Get summoner info using LoLWatcher
@watcher_router.get("/lol_watcher/summoner/{summoner_name}")
async def get_watcher_summoner_info(summoner_name: str, region: str = "na1"):
    lol_watcher = LolWatcher(RIOT_API_KEY)
    summoner = lol_watcher.summoner.by_name(region, summoner_name)
    return summoner

@watcher_router.get('/lol_watcher/match_history/<puuid>')
async def match_history(puuid):
    matches = lol_watcher.match.matchlist_by_puuid(region, puuid, queue=420)
    return matches

@watcher_router.get('/lol_watcher/analyze_matches')
async def analyze_matches(summoner_name: str, region: str = "na1"):
    summoner = lol_watcher.summoner.by_name(region, summoner_name)
    matches = lol_watcher.match.matchlist_by_puuid(region, summoner['puuid'],queue=420)

    total_matches = len(matches)
    wins = 0
    game_duration_sum = 0
    kills_sum = 0
    deaths_sum = 0
    assists_sum = 0
    gold_earned_sum = 0
    total_damage_sum = 0
    vision_score_sum = 0
    turret_kills_sum = 0
    dragon_kills_sum = 0
    baron_kills_sum = 0
    riftHerald_takedowns_sum = 0
    lane_minions_first10_minutes_sum = 0
    gold_per_minute_sum = 0

    for match in matches:
        match_id = match
        match_details = lol_watcher.match.by_id(region, match_id)
        participants = match_details['info']['participants']

        for participant in participants:
            if participant['puuid'] == summoner['puuid']:
                if participant['win']:
                    wins += 1

                game_duration_sum += match_details['info']['gameDuration']
                kills_sum += participant['kills']
                deaths_sum += participant['deaths']
                assists_sum += participant['assists']
                gold_earned_sum += participant['goldEarned']
                total_damage_sum += participant['totalDamageDealtToChampions']
                vision_score_sum += participant['visionScore']
                turret_kills_sum += participant['turretKills']
                dragon_kills_sum += participant['dragonKills']
                baron_kills_sum += participant['baronKills']
                riftHerald_takedowns_sum += participant['challenges']['riftHeraldTakedowns']
                lane_minions_first10_minutes_sum += participant['challenges']['laneMinionsFirst10Minutes']
                gold_per_minute_sum += participant['challenges']['goldPerMinute']

    # Calculate average statistics
    average_game_duration = game_duration_sum / total_matches if total_matches > 0 else 0.0
    average_kills = kills_sum / total_matches if total_matches > 0 else 0.0
    average_deaths = deaths_sum / total_matches if total_matches > 0 else 0.0
    average_assists = assists_sum / total_matches if total_matches > 0 else 0.0
    average_gold_earned = gold_earned_sum / total_matches if total_matches > 0 else 0.0
    average_total_damage = total_damage_sum / total_matches if total_matches > 0 else 0.0
    average_vision_score = vision_score_sum / total_matches if total_matches > 0 else 0.0
    average_turret_kills = turret_kills_sum / total_matches if total_matches > 0 else 0.0
    average_dragon_kills = dragon_kills_sum / total_matches if total_matches > 0 else 0.0
    average_baron_kills = baron_kills_sum / total_matches if total_matches > 0 else 0.0
    average_riftHerald_takedowns = riftHerald_takedowns_sum / total_matches if total_matches > 0 else 0.0
    average_lane_minions_first10_minutes = lane_minions_first10_minutes_sum / total_matches if total_matches > 0 else 0.0
    average_gold_per_minute = gold_per_minute_sum / total_matches if total_matches > 0 else 0.0

    # Perform analysis and prediction based on the aggregated data
    win_rate = wins / total_matches if total_matches > 0 else 0.0

    # Normalization Function
    def normalize(value, max_value):
        return value / max_value if max_value > 0 else 0.0

    weights = {
        'win_rate': 0.7,
        'average_kills': 0.2,
        'average_deaths': -0.4,
        'average_assists': 0.1,
        'average_gold_earned': 0.025,
        'average_total_damage': 0.1,
        'average_vision_score': 0.05,
        'average_turret_kills': 0.025,
        'average_dragon_kills': 0.025,
        'average_baron_kills': 0.025,
        'average_riftHerald_takedowns': 0.025,
        'average_lane_minions_first10_minutes': 0.05,
        'average_gold_per_minute': 0.025,
    }

    # the maximum values that each factor can take
    max_values = {
        'win_rate': 1.0,
        'average_kills': 52,
        'average_deaths': 31,
        'average_assists': 61,
        'average_gold_earned': 37652,
        'average_total_damage': 129365,
        'average_vision_score': 188,
        'average_turret_kills': 10,
        'average_dragon_kills': 7,
        'average_baron_kills': 5,
        'average_riftHerald_takedowns': 2,
        'average_lane_minions_first10_minutes': 120,
        'average_gold_per_minute': 1000,
        # add maximum values for other factors here
    }

    adjusted_win_rate = 0.0

    for factor, weight in weights.items():
        adjusted_win_rate += normalize(locals()[factor], max_values.get(factor, 1)) * weight

    # Restricting probability between 0 and 100
    probability = min(max(adjusted_win_rate * 100, 0), 100)

    return dict(
        total_matches=total_matches,
        probability=probability,
        average_game_duration=average_game_duration /60,
        average_kills=average_kills,
        average_deaths=average_deaths,
        average_assists=average_assists,
        average_gold_earned=average_gold_earned,
        average_total_damage=average_total_damage,
        average_vision_score=average_vision_score,
        average_turret_kills=average_turret_kills,
        average_dragon_kills=average_dragon_kills,
        average_baron_kills=average_baron_kills,
        average_riftHerald_takedowns=average_riftHerald_takedowns,
        average_lane_minions_first10_minutes=average_lane_minions_first10_minutes,
        average_gold_per_minute=average_gold_per_minute
    )
