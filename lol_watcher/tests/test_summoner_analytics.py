import sqlite3
import unittest

from summoner_analytics import fetch_and_store_detailed_summoner_matches


class TestSummonerAnalytics(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Connect to the database and create a cursor
        self.conn = sqlite3.connect("lol_summoner.db")
        self.cursor = self.conn.cursor()

    async def asyncTearDown(self):
        # Close the database connection
        self.conn.close()

    async def test_fetch_and_store_detailed_summoner_matches(self):
        # Call the function with a test summoner name and region
        await fetch_and_store_detailed_summoner_matches("gameb0x")

        # Check that the data was stored in the database
        self.cursor.execute(
            "SELECT * FROM summoner_match_data WHERE summoner_id = ?",
            ("gameb0x",),
        )
        rows = self.cursor.fetchall()

        # Assert that at least one row was returned
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()
