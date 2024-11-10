from typing import Dict

import numpy as np
from fastapi import APIRouter, Depends
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import ChampionMastery, LeagueInfo, MatchData, get_db
from riot_api_wrapper import RiotAPIWrapper

router = APIRouter()


@router.get(
    "/analytics/summoner-performance/{region}/{summoner_name}",
    response_model=Dict[str, Any],
)
async def get_summoner_performance(
    region: str, summoner_name: str, api_key: str, db: AsyncSession = Depends(get_db)
):
    """
    Analyzes and returns the performance metrics of a given summoner.
    """
    # Initialize the Riot API Wrapper
    riot_api = RiotAPIWrapper(api_key)

    # Fetch summoner data from Riot API
    summoner_data = riot_api.get_summoner_by_name(region, summoner_name)
    summoner_id = summoner_data["id"]

    # Fetch all required data in a single query
    data = await db.execute(
        select(ChampionMastery, LeagueInfo, MatchData)
        .join(ChampionMastery, ChampionMastery.summoner_id == summoner_id)
        .join(LeagueInfo, LeagueInfo.summoner_id == summoner_id)
        .join(MatchData, MatchData.summoner_id == summoner_id)
    )
    data = data.scalars().all()

    # Example analysis: Calculate average mastery level
    avg_mastery_level = np.mean([mastery.mastery_level for mastery, _, _ in data])

    # Example analysis: Calculate win rate
    wins = sum(league.wins for _, league, _ in data)
    losses = sum(league.losses for _, league, _ in data)
    win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0

    # Example analysis: Cluster match performances
    # Note: This is a simplified example. You would need to extract and preprocess match performance metrics.
    match_features = np.array(
        [[match.kills, match.deaths, match.assists] for _, _, match in data]
    )
    scaler = StandardScaler().fit(match_features)
    match_features_scaled = scaler.transform(match_features)
    n_clusters = 3  # Adjust the number of clusters as needed
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(match_features_scaled)
    performance_clusters = kmeans.labels_

    return {
        "summoner_name": summoner_name,
        "average_mastery_level": avg_mastery_level,
        "win_rate": win_rate,
        "performance_clusters": performance_clusters.tolist(),
    }
