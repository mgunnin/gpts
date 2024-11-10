from pydantic import BaseModel
from typing import Optional, List


# Model for Summoner data
class Summoner(BaseModel):
    summoner_name: str
    region: str
    profile_icon_id: Optional[int] = None
    summoner_level: Optional[int] = None


# Model for Champion Mastery data
class ChampionMastery(BaseModel):
    summoner_id: int
    champion_id: int
    mastery_level: Optional[int] = None
    mastery_points: Optional[int] = None


# Model for League Information
class LeagueInfo(BaseModel):
    summoner_id: int
    queue_type: str
    rank: str
    tier: str
    league_points: int
    wins: int
    losses: int


# Model for Match Data
class MatchData(BaseModel):
    match_id: str
    summoner_id: int
    champion_id: int
    queue_id: int
    season_id: int
    timestamp: int
    role: str
    lane: str


# Model for Player Performance
class PlayerPerformance(BaseModel):
    match_id: str
    summoner_id: int
    kills: int
    deaths: int
    assists: int
    champion_played: int
    win: bool


# Model for storing API Rate Limiting information
class RateLimit(BaseModel):
    requests: int
    time_window: int


# Model for User Authentication
class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    is_active: Optional[bool] = True


# Model for storing analytics data
class AnalyticsData(BaseModel):
    summoner_id: int
    analysis_type: str
    data: dict


# Model for storing scheduling information
class ScheduleTask(BaseModel):
    task_id: str
    task_description: str
    next_run_time: Optional[str] = None


# Additional models can be added as needed for the project's expansion
