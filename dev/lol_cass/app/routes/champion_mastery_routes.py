from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.riot import get_champion_masteries, get_summoner_by_name
from app.db.database import AsyncSessionLocal
from app.models.champion_mastery import ChampionMastery
from app.models.summoner import Summoner

router = APIRouter(prefix="/champion-masteries", tags=["Champion Masteries"])


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@router.get("/{name}/{region}")
async def get_summoner_champion_masteries(
    name: str, region: str, db: Session = Depends(get_db)
):
    summoner = get_summoner_by_name(name, region)
    masteries = get_champion_masteries(summoner)

    db_summoner = db.query(Summoner).filter(Summoner.id == summoner.id).first()
    if not db_summoner:
        db_summoner = Summoner(
            summoner_id=summoner.id,
            account_id=summoner.account_id,
            puuid=summoner.puuid,
            summoner_name=summoner.name,
            profile_icon_id=summoner.profile_icon,
            summoner_level=summoner.level,
            region=region,
        )
        db.add(db_summoner)
        db.commit()

    db_masteries = []
    for mastery in masteries:
        db_mastery = ChampionMastery(
            summoner_id=db_summoner.id,
            champion_id=mastery.champion_id,
            champion_level=mastery.champion_level,
            champion_points=mastery.champion_points,
            last_play_time=mastery.last_play_time,
            champion_points_until_next_level=mastery.champion_points_until_next_level,
            chest_granted=mastery.chest_granted,
            tokens_earned=mastery.tokens_earned,
        )
        db_masteries.append(db_mastery)

    await db.bulk_save_objects(db_masteries)
    await db.commit()
    return db_masteries
