import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.database import LeagueInfo, Summoner, get_db
from riot_api_wrapper import RiotAPIWrapper

router = APIRouter()


class LeagueInfoBase(BaseModel):
    summoner_id: int
    queue_type: str
    rank: str
    tier: str
    league_points: int
    wins: int
    losses: int


@router.get("/league-info/{summoner_name}", response_model=List[LeagueInfoBase])
async def get_league_info(
    summoner_name: str, region: str, db: AsyncSession = Depends(get_db)
):
    async with db as session:
        # Fetch the summoner from the database
        stmt = (
            select(Summoner)
            .options(selectinload(Summoner.league_info))
            .where(Summoner.summoner_name == summoner_name, Summoner.region == region)
        )
        result = await session.execute(stmt)
        summoner: Optional[Summoner] = result.scalars().first()

        if summoner is None:
            raise HTTPException(status_code=404, detail="Summoner not found")

        # If the summoner is found but has no league info, fetch from Riot API and update the database
        if not summoner.league_info:
            riot_api = RiotAPIWrapper(os.environ.get("RIOT_API_KEY"))
            league_info_data = riot_api.get_league_info_by_summoner(region, summoner.id)
            for info in league_info_data:
                league_info = LeagueInfo(
                    summoner_id=summoner.id,
                    queue_type=info.get("queueType"),
                    rank=info.get("rank"),
                    tier=info.get("tier"),
                    league_points=info.get("leaguePoints"),
                    wins=info.get("wins"),
                    losses=info.get("losses"),
                )
                session.add(league_info)
            await session.commit()

            # Fetch again after updating
            stmt = (
                select(Summoner)
                .options(selectinload(Summoner.league_info))
                .where(
                    Summoner.summoner_name == summoner_name, Summoner.region == region
                )
            )
            result = await session.execute(stmt)
            summoner: Optional[Summoner] = result.scalars().first()

        return summoner.league_info
