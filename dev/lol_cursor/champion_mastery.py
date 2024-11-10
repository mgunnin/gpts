import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import ChampionMastery, Summoner, get_db
from riot_api_wrapper import RiotAPIWrapper

router = APIRouter()

riot_api = RiotAPIWrapper(os.environ["RIOT_API_KEY"])


@router.get("/champion-mastery/{summoner_name}/{region}", response_model=List[dict])
async def get_champion_mastery(
    summoner_name: str, region: str, db: AsyncSession = Depends(get_db)
):

    # Fetch summoner information to get the summoner ID
    summoner_info = riot_api.get_summoner_by_name(region, summoner_name)
    if not summoner_info:
        raise HTTPException(status_code=404, detail="Summoner not found")

    # Check if the summoner is already in the database
    db_summoner = (
        (
            await db.execute(
                select(Summoner).filter(
                    Summoner.summoner_name == summoner_name, Summoner.region == region
                )
            )
        )
        .scalars()
        .first()
    )
    if not db_summoner:
        # If not, add the summoner to the database
        db_summoner = Summoner(
            name=summoner_info["name"],
            region=region,
            profile_icon_id=summoner_info["profileIconId"],
            summoner_level=summoner_info["summonerLevel"],
        )
        db.add(db_summoner)
        await db.commit()
        await db.refresh(db_summoner)

    # Fetch champion mastery information using the Riot API
    champion_masteries = riot_api.get_champion_mastery_by_summoner(
        region, summoner_info["id"]
    )

    # Store or update champion mastery information in the database
    for mastery in champion_masteries:
        db_mastery = (
            (
                await db.execute(
                    select(ChampionMastery).filter(
                        ChampionMastery.summoner_id == db_summoner.id,
                        ChampionMastery.champion_id == mastery["championId"],
                    )
                )
            )
            .scalars()
            .first()
        )
        if db_mastery:
            db_mastery.mastery_level = mastery["championLevel"]
            db_mastery.mastery_points = mastery["championPoints"]
        else:
            new_mastery = ChampionMastery(
                summoner_id=db_summoner.id,
                champion_id=mastery["championId"],
                mastery_level=mastery["championLevel"],
                mastery_points=mastery["championPoints"],
            )
            db.add(new_mastery)
    await db.commit()

    # Return the champion mastery information
    return champion_masteries
