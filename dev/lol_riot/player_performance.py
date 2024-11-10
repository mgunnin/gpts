from typing import List, Dict
from database import Database
from riot_api_wrapper import RiotAPIWrapper
from models import MatchData


class PlayerPerformanceManager:
    def __init__(self, db: Database, api_wrapper: RiotAPIWrapper):
        self.db = db
        self.api_wrapper = api_wrapper

    def calculate_performance_metrics(
        self, summoner_name: str, region: str
    ) -> Dict[str, float]:
        """Calculates performance metrics for a given summoner."""
        summoner = self.api_wrapper.get_summoner_by_name(region, summoner_name)
        puuid = summoner.get("puuid")
        match_ids = self.api_wrapper.get_match_ids(region, puuid, count=20)

        total_kills = 0
        total_deaths = 0
        total_assists = 0
        total_damage_dealt = 0
        total_games = len(match_ids)

        for match_id in match_ids:
            match_details = self.api_wrapper.get_match_details(region, match_id)
            participants = match_details.get("info", {}).get("participants", [])
            for participant in participants:
                if participant.get("puuid") == puuid:
                    total_kills += participant.get("kills", 0)
                    total_deaths += participant.get("deaths", 0)
                    total_assists += participant.get("assists", 0)
                    total_damage_dealt += participant.get(
                        "totalDamageDealtToChampions", 0
                    )
                    break

        # Avoid division by zero
        if total_games == 0:
            return {}

        # Calculate averages
        avg_kills = total_kills / total_games
        avg_deaths = total_deaths / total_games
        avg_assists = total_assists / total_games
        avg_damage_dealt = total_damage_dealt / total_games

        return {
            "average_kills": avg_kills,
            "average_deaths": avg_deaths,
            "average_assists": avg_assists,
            "average_damage_dealt": avg_damage_dealt,
        }

    def store_performance_metrics(self, summoner_name: str, region: str):
        """Stores performance metrics for a given summoner in the database."""
        metrics = self.calculate_performance_metrics(summoner_name, region)
        if metrics:
            query = """
            INSERT INTO player_performance (summoner_name, region, average_kills, average_deaths, average_assists, average_damage_dealt)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (summoner_name, region) DO UPDATE
            SET average_kills = EXCLUDED.average_kills,
                average_deaths = EXCLUDED.average_deaths,
                average_assists = EXCLUDED.average_assists,
                average_damage_dealt = EXCLUDED.average_damage_dealt;
            """
            params = (
                summoner_name,
                region,
                metrics["average_kills"],
                metrics["average_deaths"],
                metrics["average_assists"],
                metrics["average_damage_dealt"],
            )
            self.db.execute_query(query, params)


# Example usage
if __name__ == "__main__":
    db = Database()
    db.connect()
    api_wrapper = RiotAPIWrapper()
    performance_manager = PlayerPerformanceManager(db, api_wrapper)
    performance_manager.store_performance_metrics("ExampleSummoner", "NA1")
