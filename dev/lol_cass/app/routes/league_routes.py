from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.api.riot import get_league_entries, get_summoner_by_name
from app.db.database import AsyncSessionLocal
from app.models.league import League
from app.models.summoner import Summoner

router = APIRouter(prefix="/leagues", tags=["Leagues"])


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@router.get("/{name}/{region}")
async def get_summoner_league_entries(
    name: str, region: str, db: Session = Depends(get_db)
):
    summoner = get_summoner_by_name(name, region)
    league_entries = get_league_entries(summoner)

    result = db.execute(
        select(Summoner).filter(Summoner.summoner_id == summoner.id)
    )
    db_summoner = result.scalars().first()
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
        await db.commit()

    db_league_entries = []
    for entry in league_entries:
        db_entry = League(
            summoner_id=db_summoner.summoner_id,
            queue=entry.queue,
            tier=entry.tier,
            league_points=entry.league_points,
            wins=entry.wins,
            losses=entry.losses,
            hot_streak=entry.hot_streak,
            veteran=entry.veteran,
            fresh_blood=entry.fresh_blood,
            inactive=entry.inactive,
        )
        db_league_entries.append(db_entry)

    for db_league_entry in db_league_entries:
        db.add(db_league_entry)
    await db.commit()
