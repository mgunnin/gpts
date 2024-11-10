import asyncio
import os
from typing import List

from sqlalchemy import select

from database.database import ChampionMastery, LeagueInfo, Summoner, get_db
from match_data import MatchDataHandler
from riot_api_wrapper import RiotAPIWrapper

REGIONS = ["NA1", "EUW1", "EUN1", "KR"]
TOP_PLAYERS_COUNT = 50


async def populate_summoner_data(
    riot_api: RiotAPIWrapper, region: str, summoner_name: str
) -> None:
    """
    Fetches and populates the database with summoner data.
    """
    async with get_db() as session:
        summoner_info = riot_api.get_summoner_by_name(region, summoner_name)
        result = await session.execute(
            select(Summoner).filter_by(puuid=summoner_info["puuid"])
        )
        existing_summoner = result.scalars().first()

        if existing_summoner:
            # Update existing summoner's data
            existing_summoner.summoner_name = summoner_info["name"]
            existing_summoner.region = region
            existing_summoner.profile_icon_id = summoner_info["profileIconId"]
            existing_summoner.summoner_level = summoner_info["summonerLevel"]
            existing_summoner.summoner_id = summoner_info["id"]
            existing_summoner.account_id = summoner_info["accountId"]
            summoner_id = existing_summoner.id
        else:
            # Insert new summoner
            new_summoner = Summoner(
                summoner_name=summoner_info["name"],
                region=region,
                profile_icon_id=summoner_info["profileIconId"],
                summoner_level=summoner_info["summonerLevel"],
                puuid=summoner_info["puuid"],
                summoner_id=summoner_info["id"],
                account_id=summoner_info["accountId"],
            )
            session.add(new_summoner)
            await session.flush()
            summoner_id = new_summoner.id

        puuid = summoner_info["puuid"]
        summoner_id = summoner_info["id"]
        await session.commit()

        match_data_handler = MatchDataHandler(riot_api)
        await match_data_handler.fetch_match_data(region, puuid)
        await populate_champion_mastery(riot_api, region, puuid)
        await populate_league_info(riot_api, region, summoner_id)


async def populate_champion_mastery(riot_api: RiotAPIWrapper, region: str, puuid: str):
    """
    Fetches and populates the database with champion mastery data.
    """
    async with get_db() as session:
        masteries = riot_api.get_champion_mastery_by_summoner(region, puuid)
        for mastery in masteries:
            existing_mastery = await session.execute(
                select(ChampionMastery).filter_by(
                    puuid=puuid, champion_id=mastery["championId"]
                )
            )
            existing_mastery = existing_mastery.scalars().first()
            if existing_mastery:
                existing_mastery.mastery_level = mastery["championLevel"]
                existing_mastery.mastery_points = mastery["championPoints"]
            else:
                new_mastery = ChampionMastery(
                    puuid=puuid,
                    champion_id=mastery["championId"],
                    mastery_level=mastery["championLevel"],
                    mastery_points=mastery["championPoints"],
                )
                session.add(new_mastery)
        await session.commit()


async def populate_league_info(riot_api: RiotAPIWrapper, region: str, summoner_id: str):
    """
    Fetches and populates the database with league information.
    """
    async with get_db() as session:
        leagues = riot_api.get_league_info_by_summoner(region, summoner_id)
        for league in leagues:
            result = await session.execute(
                select(LeagueInfo).filter_by(
                    summoner_id=summoner_id, queue_type=league["queueType"]
                )
            )
            existing_league_info = result.scalars().first()
            if existing_league_info:
                existing_league_info.rank = league["rank"]
                existing_league_info.tier = league["tier"]
                existing_league_info.league_points = league["leaguePoints"]
                existing_league_info.wins = league["wins"]
                existing_league_info.losses = league["losses"]
            else:
                new_league_info = LeagueInfo(
                    summoner_id=summoner_id,
                    queue_type=league["queueType"],
                    rank=league["rank"],
                    tier=league["tier"],
                    league_points=league["leaguePoints"],
                    wins=league["wins"],
                    losses=league["losses"],
                )
                session.add(new_league_info)
        await session.commit()


async def fetch_top_players(riot_api: RiotAPIWrapper, region: str) -> None:
    """
    Fetches and populates the database with the top players' data from a specific region.
    """
    top_player_names = riot_api.get_top_players(region, TOP_PLAYERS_COUNT)

    for player_name in top_player_names:
        await populate_summoner_data(riot_api, region, player_name)

        # Fetch the newly added summoner from the database to get the internal summoner_id
        async with get_db() as db:
            result = await db.execute(
                select(Summoner).filter_by(name=player_name, region=region)
            )
            summoner = result.scalars().first()
            if summoner:
                # Populate champion mastery, league info, and match data for the summoner
                await populate_champion_mastery(riot_api, region, summoner.puuid)
                await populate_league_info(riot_api, region, summoner.summoner_id)
                await MatchDataHandler(riot_api).fetch_match_data(
                    region, summoner.puuid
                )


async def main():
    """
    Main function to run the data population process.
    """
    api_key = os.environ.get("RIOT_API_KEY")
    if api_key is None:
        raise ValueError("API key is required")
    riot_api = RiotAPIWrapper(api_key)

    for region in REGIONS:
        await fetch_top_players(riot_api, region)


if __name__ == "__main__":
    asyncio.run(main())
