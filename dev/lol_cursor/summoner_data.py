import os
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import Summoner, get_db
from riot_api_wrapper import RiotAPIWrapper

router = APIRouter()


@router.get("/summoner/{region}/{summoner_name}", response_model=Dict[str, str])
async def get_summoner_data(
    region: str, summoner_name: str, db: AsyncSession = Depends(get_db)
):
    """
    Fetches summoner data from the Riot Games API and stores/updates it in the database.
    Returns the summoner data.
    """
    # Initialize the Riot API Wrapper
    riot_api = RiotAPIWrapper(api_key=os.environ.get("RIOT_API_KEY") or "")
    if not riot_api.api_key:
        raise ValueError("API key is required")

    # Fetch summoner data from Riot API
    summoner_data = riot_api.get_summoner_by_name(region, summoner_name)

    # Check if summoner already exists in the database
    async with db as session:
        result = await session.execute(
            select(Summoner).filter_by(name=summoner_name, region=region)
        )
        existing_summoner = result.scalars().first()

        if existing_summoner:
            # Update existing summoner data
            existing_summoner.profile_icon_id = summoner_data.get("profileIconId")
            existing_summoner.summoner_level = summoner_data.get("summonerLevel")
        else:
            # Insert new summoner data into the database
            new_summoner = Summoner(
                name=summoner_data.get("name"),
                region=region,
                profile_icon_id=summoner_data.get("profileIconId"),
                summoner_level=summoner_data.get("summonerLevel"),
            )
            session.add(new_summoner)

        await session.commit()

    # Return the fetched summoner data
    return summoner_data
