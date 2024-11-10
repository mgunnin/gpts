import pandas as pd
from database import Database
from models import Summoner, ChampionMastery, LeagueInfo, MatchData
from typing import List, Dict


class AnalyticsManager:
    def __init__(self, db: Database):
        self.db = db

    def get_summoner_performance_over_time(self, summoner_id: int) -> pd.DataFrame:
        """
        Fetches and analyzes summoner performance over time.
        Returns a DataFrame with match dates and key performance metrics.
        """
        query = """
        SELECT match_date, kills, deaths, assists, win
        FROM match_data
        WHERE summoner_id = %s
        ORDER BY match_date ASC;
        """
        match_data = self.db.execute_query(query, (summoner_id,), fetch=True)
        df = pd.DataFrame(match_data)
        df["KDA"] = (df["kills"] + df["assists"]) / df["deaths"].replace({0: 1})
        return df

    def get_champion_mastery_distribution(self, summoner_id: int) -> pd.DataFrame:
        """
        Fetches champion mastery details for a given summoner and returns a DataFrame
        with champion IDs and their corresponding mastery points.
        """
        query = """
        SELECT champion_id, mastery_points
        FROM champion_mastery
        WHERE summoner_id = %s;
        """
        mastery_data = self.db.execute_query(query, (summoner_id,), fetch=True)
        df = pd.DataFrame(mastery_data)
        return df

    def get_win_rate_by_champion(self, summoner_id: int) -> pd.DataFrame:
        """
        Calculates and returns the win rate by champion for a given summoner.
        """
        query = """
        SELECT champion_id, COUNT(*) AS games, SUM(CASE WHEN win THEN 1 ELSE 0 END) AS wins
        FROM match_data
        WHERE summoner_id = %s
        GROUP BY champion_id;
        """
        win_data = self.db.execute_query(query, (summoner_id,), fetch=True)
        df = pd.DataFrame(win_data)
        df["win_rate"] = df["wins"] / df["games"]
        return df

    def get_league_distribution(self) -> pd.DataFrame:
        """
        Fetches and analyzes the distribution of players across different leagues and ranks.
        Returns a DataFrame with league, rank, and the count of players.
        """
        query = """
        SELECT tier, rank, COUNT(*) AS player_count
        FROM league_info
        GROUP BY tier, rank
        ORDER BY tier DESC, rank;
        """
        league_data = self.db.execute_query(query, fetch=True)
        df = pd.DataFrame(league_data)
        return df


# Example usage
if __name__ == "__main__":
    db = Database()
    db.connect()
    analytics_manager = AnalyticsManager(db)
    summoner_id = 1  # Example summoner ID
    print(analytics_manager.get_summoner_performance_over_time(summoner_id))
    print(analytics_manager.get_champion_mastery_distribution(summoner_id))
    print(analytics_manager.get_win_rate_by_champion(summoner_id))
    print(analytics_manager.get_league_distribution())
