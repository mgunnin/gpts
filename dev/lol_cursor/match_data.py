import os
from typing import Any, Dict

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.database import MatchData, Summoner, get_db
from riot_api_wrapper import RiotAPIWrapper


class MatchDataHandler:
    def __init__(self, riot_api: RiotAPIWrapper):
        self.riot_api = riot_api

    async def fetch_and_store_summoner_data(self, region: str, puuid: str, db: Session):
        stmt = select(Summoner).filter_by(puuid=puuid)
        result = db.execute(stmt)
        summoner = result.scalars().first()
        if not summoner:
            summoner_info = self.riot_api.get_summoner_by_puuid(region, puuid)
            new_summoner = Summoner(
                summoner_name=summoner_info["name"],
                region=region,
                profile_icon_id=summoner_info["profileIconId"],
                summoner_level=summoner_info["summonerLevel"],
                puuid=puuid,
                summoner_id=summoner_info["id"],
                account_id=summoner_info["accountId"],
            )
            db.add(new_summoner)
            db.commit()

    async def store_match_data(self, match_details: Dict[str, Any], db: Session):
        match_data_list = []
        for participant in match_details["info"]["participants"]:
            match_data = MatchData(
                puuid=participant["puuid"],
                match_id=match_details["metadata"]["matchId"],
                game_creation=match_details["info"]["gameCreation"],
                game_duration=match_details["info"]["gameDuration"],
                queue_id=match_details["info"]["queueId"],
                champion_id=participant["championId"],
                champion_name=participant["championName"],
                team_id=participant["teamId"],
                win=participant["win"],
                kills=participant["kills"],
                deaths=participant["deaths"],
                assists=participant["assists"],
                total_damage_dealt_to_champions=participant[
                    "totalDamageDealtToChampions"
                ],
                total_damage_taken=participant["totalDamageTaken"],
                vision_score=participant["visionScore"],
                gold_earned=participant["goldEarned"],
                total_minions_killed=participant["totalMinionsKilled"],
            )
            match_data_list.append(match_data)
        db.add_all(match_data_list)
        db.commit()

    async def fetch_match_data(
        self, region: str, puuid: str, start: int = 0, count: int = 20
    ):
        matchlist = self.riot_api.get_matchlist_by_puuid(region, puuid, start, count)
        async with get_db() as db:
            for match in matchlist:
                match_details = match["details"]
                if match_details is None:
                    continue
                await self.store_match_data(match_details, db)
                for participant in match_details["info"]["participants"]:
                    participant_puuid = participant["puuid"]
                    await self.fetch_and_store_summoner_data(
                        region, participant_puuid, db
                    )


if __name__ == "__main__":
    api_key = os.environ.get("RIOT_API_KEY")
    if api_key is None:
        raise ValueError("API key is required")
    riot_api = RiotAPIWrapper(api_key)
    match_data_handler = MatchDataHandler(riot_api)
