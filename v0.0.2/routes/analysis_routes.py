from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter
from models import SummonerData

router = APIRouter()

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

@router.post("/analyze_match_data/{puuid}")
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
        total_kills += match.kills
        total_deaths += match.deaths
        total_assists += match.assists
        total_gold_per_minute += match.goldPerMinute
        total_damage_per_minute += match.damagePerMinute
        total_kill_participation += match.killParticipation
        total_heal += match.totalHeal
        total_damage_dealt_to_champions += match.totalDamageDealtToChampions
        total_vision_score += match.visionScore

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