from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.riot import get_match
from app.db.database import AsyncSessionLocal
from app.models.match import Match

router = APIRouter(prefix="/matches", tags=["Matches"])


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@router.get("/{match_id}/{region}")
async def get_match_details(match_id: int, region: str, db: Session = Depends(get_db)):
    match = get_match(match_id, region)
    db_match = Match(
        match_id=match.id,
        region=region,
        platform_id=match.platform.value,
        game_id=match.game_id,
        champion_id=match.champion_id,
        queue_id=match.queue_id,
        season_id=match.season_id,
        timestamp=match.creation.timestamp(),
        role=match.role.value,
        lane=match.lane.value,
    )
    await db.merge(db_match)
    await db.commit()
    return db_match
