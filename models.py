from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Region(str, Enum):
    na1 = "na1"
    br1 = "br1"
    eun1 = "eun1"
    euw1 = "euw1"
    jp1 = "jp1"
    kr = "kr"


class MassRegion(str, Enum):
    americas = "americas"
    europe = "europe"
    asia = "asia"
    sea = "sea"


class PlayerStats(BaseModel):
    assists: int = Field(..., description="Number of assists made by the player")
    deaths: int = Field(..., description="Number of deaths of the player")
    kills: int = Field(..., description="Number of kills made by the player")
    gold_per_minute: float = Field(
        ..., description="Gold earned per minute by the player"
    )
    damage_per_minute: float = Field(
        ..., description="Damage dealt per minute by the player"
    )
    kill_participation: float = Field(
        ..., description="Kill participation rate of the player"
    )
    total_heal: int = Field(..., description="Total healing done by the player")
    total_damage_dealt_to_champions: int = Field(
        ..., description="Total damage dealt to champions by the player"
    )
    vision_score: int = Field(..., description="Vision score of the player")
    wards_placed: int = Field(..., description="Number of wards placed by the player")
    gold_earned: int = Field(..., description="Total gold earned by the player")
    gold_spent: int = Field(..., description="Total gold spent by the player")


class Match(BaseModel):
    game_id: int = Field(..., description="Game ID")
    platform_id: str = Field(..., description="Platform ID")
    game_creation: int = Field(..., description="Game creation timestamp")
    game_duration: int = Field(..., description="Game duration in seconds")
    queue_id: int = Field(..., description="Queue ID")
    map_id: int = Field(..., description="Map ID")
    season_id: int = Field(..., description="Season ID")
    game_version: str = Field(..., description="Game version")
    game_mode: str = Field(..., description="Game mode")
    game_type: str = Field(..., description="Game type")
    teams: List[dict] = Field(..., description="List of team data")
    participants: List[PlayerStats] = Field(..., description="List of participant data")
    participant_identities: List[dict] = Field(
        ..., description="List of participant identities"
    )


class SummonerData(BaseModel):
    matches: List[Match] = Field(..., description="List of matches")
    summoner_name: str = Field(..., description="Summoner name")
    summoner_id: str = Field(..., description="Summoner ID")
    account_id: str = Field(..., description="Account ID")
    puuid: str = Field(..., description="PUUID")
    region: str = Field(..., description="Region")
    tier: str = Field(..., description="Tier")
    rank: str = Field(..., description="Rank")
    league_points: int = Field(..., description="League points")
    wins: int = Field(..., description="Wins")
    losses: int = Field(..., description="Losses")
    win_rate: float = Field(..., description="Win rate")
