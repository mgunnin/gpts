import asyncio
import csv
import os

import aiosqlite
import cassiopeia as cass
from cassiopeia import MatchHistory, Queue, Summoner
from dotenv import load_dotenv

from models import MassRegion, Region
from utils import get_api_response

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
RIOT_API_BASE_URL = os.getenv("RIOT_API_BASE_URL")


# Connect to SQLite database (or create it if it doesn't exist)
async def create_db():
    async with aiosqlite.connect("lol_summoner.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS top_champion_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summoner_name TEXT NOT NULL,
                region TEXT NOT NULL,
                puuid TEXT UNIQUE NOT NULL,
                account_id TEXT,
                profile_icon_id INTEGER,
                UNIQUE(summoner_name, region)
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS champion_rank (
                summoner_id INTEGER NOT NULL,
                champion TEXT NOT NULL,
                rank INTEGER NOT NULL,
                tier TEXT NOT NULL,
                FOREIGN KEY(summoner_id) REFERENCES top_champion_players(id)
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS match_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puuid TEXT NOT NULL,
                match_id TEXT NOT NULL,
                game_creation INTEGER NOT NULL,
                champion_name TEXT NOT NULL,
                kills INTEGER NOT NULL,
                deaths INTEGER NOT NULL,
                assists INTEGER NOT NULL,
                total_damage_dealt_to_champions INTEGER NOT NULL,
                vision_score INTEGER NOT NULL,
                gold_earned INTEGER NOT NULL,
                total_minions_killed INTEGER NOT NULL,
                role TEXT NOT NULL,
                win BOOLEAN NOT NULL,
                FOREIGN KEY(puuid) REFERENCES top_champion_players(puuid)
            )
            """
        )
        await db.commit()


# Load top players data from a CSV file and store it in the database
async def load_top_players_data(csv_file_path):
    async with aiosqlite.connect("lol_summoner.db") as db:
        with open(csv_file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                puuid, account_id, profile_icon_id = await fetch_summoner_details(
                    row["Summoner"]
                )
                if puuid:
                    await db.execute(
                        """
                        INSERT OR IGNORE INTO top_champion_players (summoner_name, region, puuid, account_id, profile_icon_id)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            row["Summoner"],
                            row["Region"],
                            puuid,
                            account_id,
                            profile_icon_id,
                        ),
                    )
                    summoner_id = await db.execute(
                        "SELECT id FROM top_champion_players WHERE puuid = ?", (puuid,)
                    )
                    summoner_id = await summoner_id.fetchone()
                    if summoner_id:
                        await db.execute(
                            """
                            INSERT INTO champion_rank (summoner_id, champion, rank, tier)
                            VALUES (?, ?, ?, ?)
                            """,
                            (summoner_id[0], row["Champion"], row["Rank"], row["Tier"]),
                        )
        await db.commit()


async def fetch_summoner_details(summoner_name: str, region: str = "NA"):
    summoner = cass.get_summoner(name=summoner_name, region=region)
    puuid = summoner.puuid
    account_id = summoner.account_id
    profile_icon_id = summoner.profile_icon.id
    return puuid, account_id, profile_icon_id


async def fetch_match_history(puuid: str):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"
    response_dict = await get_api_response(url, headers)
    match_ids = response_dict["data"]
    return match_ids if match_ids else []


async def store_match_history(
    puuid: str,
    match_ids: list,
):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with aiosqlite.connect("lol_summoner.db") as db:
        for match_id in match_ids:
            url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match_data = await get_api_response(url, headers)
            if match_data["status_code"] == 200:
                match_info = match_data["data"]["info"]
                participants = match_info["participants"]
                for participant in participants:
                    if participant["puuid"] == puuid:
                        await db.execute(
                            """
                            INSERT INTO match_history (puuid, match_id, game_creation, champion_name, kills, deaths, assists, total_damage_dealt_to_champions, vision_score, gold_earned, total_minions_killed, role, win)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                puuid,
                                match_id,
                                match_info["gameCreation"],
                                participant["championName"],
                                participant["kills"],
                                participant["deaths"],
                                participant["assists"],
                                participant["totalDamageDealtToChampions"],
                                participant["visionScore"],
                                participant["goldEarned"],
                                participant["totalMinionsKilled"],
                                participant["role"],
                                participant["win"],
                            ),
                        )
        await db.commit()


async def analyze_and_provide_advice(puuid: str):
    async with aiosqlite.connect("lol_summoner.db") as db:
        cursor = await db.execute(
            "SELECT kills, deaths, assists FROM match_history WHERE puuid = ?",
            (puuid,),
        )
        matches = await cursor.fetchall()
        if matches:
            avg_kills = sum(match[0] for match in matches) / len(matches)
            avg_deaths = sum(match[1] for match in matches) / len(matches)
            avg_assists = sum(match[2] for match in matches) / len(matches)
            advice = "Try to focus on staying alive and assisting your teammates more if your deaths are high."
            if avg_deaths > avg_kills:
                return advice
            else:
                return "Great job on keeping a positive KDA! Keep focusing on your objectives."
        return "No matches found to analyze."


async def main():
    await create_db()
    await load_top_players_data("datasets/lol_champion_player_ranks_testing.csv")
    # Example usage for a specific summoner
    puuid = (
        "k_BCLNxYlH8OxUwqcHOCmHvBnGUci9cFxm2uZNgOs8vI-HcLa4BD1bBTQnPGum13wlrijcdnLH801Q"
    )
    if puuid:
        match_ids = await fetch_match_history(puuid)
        await store_match_history(puuid, match_ids)
        advice = await analyze_and_provide_advice(puuid)
        print(advice)


if __name__ == "__main__":
    asyncio.run(main())
