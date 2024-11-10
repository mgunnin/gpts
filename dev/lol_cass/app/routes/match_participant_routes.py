from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.riot import get_match
from app.db.database import AsyncSessionLocal
from app.models.match_participant import MatchParticipant

router = APIRouter(prefix="/match_participants", tags=["Match Participants"])


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@router.get("/{match_id}/{region}")
async def get_match_participants(
    match_id: str, region: str, db: Session = Depends(get_db)
):
    match = get_match(int(match_id), region)
    db_participants = []
    for participant in match.participants:
        db_participant = MatchParticipant(
            match_id=match_id,
            summoner_id=participant.summoner.id,
            champion_id=participant.champion.id,
            team_id=participant.team.id,
            lane=participant.lane.value,
            role=participant.role.value,
            kills=participant.stats.kills,
            deaths=participant.stats.deaths,
            assists=participant.stats.assists,
            gold_earned=participant.stats.gold_earned,
            damage_dealt=participant.stats.total_damage_dealt_to_champions,
            damage_taken=participant.stats.total_damage_taken,
            wards_placed=participant.stats.wards_placed,
            wards_killed=participant.stats.wards_killed,
            vision_wards_bought=participant.stats.vision_wards_bought_in_game,
            cs=participant.stats.total_minions_killed
            + participant.stats.neutral_minions_killed,
            vision_score=participant.stats.vision_score,
            first_blood=participant.stats.first_blood_kill,
            first_tower=participant.stats.first_tower_assist,
            first_inhibitor=participant.stats.first_inhibitor_assist,
            first_baron=participant.stats.first_baron_kill,
            first_dragon=participant.stats.first_dragon_kill,
            first_rift_herald=participant.stats.first_rift_herald_kill,
            tower_kills=participant.stats.turret_kills,
            inhibitor_kills=participant.stats.inhibitor_kills,
            baron_kills=participant.stats.baron_kills,
            dragon_kills=participant.stats.dragon_kills,
            rift_herald_kills=participant.stats.rift_herald_kills,
            items=str([item.id for item in participant.stats.items]),
            spells=str([spell.id for spell in participant.spells]),
            runes=str([rune.id for rune in participant.runes]),
            summoner_spells=str([spell.id for spell in participant.summoner_spells]),
            win=participant.stats.win,
        )
        db_participants.append(db_participant)

    await db.bulk_save_objects(db_participants)
    await db.commit()
    return db_participants
