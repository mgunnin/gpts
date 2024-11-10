from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.api.riot import get_summoner_by_name
from app.db.database import AsyncSessionLocal
from app.models.summoner import Summoner

router = APIRouter(prefix="/summoners", tags=["Summoners"])


@lru_cache(maxsize=100)
async def get_summoner_from_cache(account_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Summoner).filter_by(account_id=account_id)
        )
        return result.scalars().first()


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@router.get("/{name}/{region}")
async def get_summoner(name: str, region: str, db: Session = Depends(get_db)):
    summoner = get_summoner_by_name(name, region)

    cached_summoner = get_summoner_from_cache(summoner.account_id)
    if cached_summoner:
        return cached_summoner

    async with db as session:
        # Check if the summoner already exists by account_id
        result = await session.execute(
            select(Summoner).filter_by(account_id=summoner.account_id)
        )
        existing_summoner = result.scalars().first()

        if existing_summoner:
            # Update the existing summoner with the new data
            existing_summoner.summoner_id = summoner.id
            existing_summoner.puuid = summoner.puuid
            existing_summoner.summoner_name = summoner.name
            existing_summoner.profile_icon_id = summoner.profile_icon
            existing_summoner.summoner_level = summoner.level
            existing_summoner.region = region
            existing_summoner.last_updated = datetime.now()

        else:
            new_summoner = Summoner(
                account_id=summoner.account_id,
                summoner_id=summoner.id,
                puuid=summoner.puuid,
                summoner_name=summoner.name,
                profile_icon_id=summoner.profile_icon.id,
                summoner_level=summoner.level,
                region=region,
                last_updated=datetime.now(),
            )
            session.add(new_summoner)

        await db.commit()

        return existing_summoner if existing_summoner else new_summoner
