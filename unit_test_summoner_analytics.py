import unittest

import asyncio
import csv
import sqlite3
from summoner_analytics import fetch_and_store_summoner_data, fetch_and_store_match_statistics, Region
import unittest

class TestSummonerAnalytics(unittest.TestCase):

  async def fetch_puuid(self, summoner):
    # Implement the logic for fetching the puuid
    pass

  async def test_fetch_and_store_summoner_data(self):
    # Arrange
    with open("datasets/lol_champion_player_ranks_1-5.csv", "r") as file:
      csv_reader = csv.DictReader(file)
      rows = list(csv_reader)

    # Act
    await fetch_and_store_summoner_data()

    # Assert
    with sqlite3.connect("lol_summoner.db") as conn:
      cursor = conn.cursor()

      for row in rows:
        region = Region[row["Region"]]
        puuid = await self.fetch_puuid(row["Summoner"])
        if puuid:
          cursor.execute(
            """
            SELECT * FROM top_champion_players WHERE champion = ? AND region = ? AND rank = ? AND tier = ? AND summoner_name = ? AND puuid = ?
            """,
            (
              row["Champion"],
              row["Region"],
              row["Rank"],
              row["Tier"],
              row["Summoner"],
              puuid,
            ),
          )
          result = cursor.fetchone()
          self.assertIsNotNone(result)

async def test_fetch_and_store_match_statistics(self):
    # Arrange
    with open("datasets/lol_champion_player_ranks_1-5.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)

    # Act
    await fetch_and_store_summoner_data()
    for row in rows:
        region = Region[row["Region"]]
        puuid = await self.fetch_puuid(row["Summoner"])
        if puuid:
            await fetch_and_store_match_statistics(puuid, {})

    # Assert
    with sqlite3.connect("lol_summoner.db") as conn:
        cursor = conn.cursor()

        for row in rows:
            region = Region[row["Region"]]
            puuid = await self.fetch_puuid(row["Summoner"])
            if puuid:
                cursor.execute(
                    """
            SELECT * FROM match_statistics WHERE puuid = ? AND match_id = ?
            """,
                    (puuid, row["Match ID"]),
                )
                result = cursor.fetchone()
                self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
