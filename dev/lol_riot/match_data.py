from typing import List

from database import Database
from models import MatchData
from riot_api_wrapper import RiotAPIWrapper


class MatchDataManager:
    def __init__(self, db: Database, api_wrapper: RiotAPIWrapper):
        self.db = db
        self.api_wrapper = api_wrapper

    def fetch_and_store_match_data(self, region: str, summoner_name: str):
        """Fetches match data for a given summoner and stores it in the database."""
        summoner = self.api_wrapper.get_summoner_by_name(region, summoner_name)
        puuid = summoner.get("puuid")
        match_ids = self.api_wrapper.get_match_ids(region, puuid)

        for match_id in match_ids:
            match_details = self.api_wrapper.get_match_details(region, match_id)
            participants = match_details.get("info", {}).get("participants", [])
            for participant in participants:
                if participant.get("puuid") == puuid:
                    match_data = MatchData(
                        match_id=match_id,
                        summoner_id=summoner.get("id"),
                        champion_id=participant.get("championId"),
                        queue_id=match_details.get("info", {}).get("queueId"),
                        season_id=match_details.get("info", {})
                        .get("gameVersion")
                        .split(".")[0],  # Simplified season extraction
                        timestamp=match_details.get("info", {}).get("gameCreation"),
                        role=participant.get("role"),
                        lane=participant.get("lane"),
                    )
                    self.store_match_data(match_data)

    def store_match_data(self, match_data: MatchData):
        """Stores match data in the database."""
        query = """
        INSERT INTO match_data (match_id, summoner_id, champion_id, queue_id, season_id, timestamp, role, lane)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id, summoner_id) DO NOTHING;
        """
        params = (
            match_data.match_id,
            match_data.summoner_id,
            match_data.champion_id,
            match_data.queue_id,
            match_data.season_id,
            match_data.timestamp,
            match_data.role,
            match_data.lane,
        )
        self.db.execute_query(query, params)


if __name__ == "__main__":
    db = Database()
    db.connect()
    api_wrapper = RiotAPIWrapper()
    match_data_manager = MatchDataManager(db, api_wrapper)

    # Example usage
    match_data_manager.fetch_and_store_match_data("NA1", "SummonerName")
