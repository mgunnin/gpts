import asyncio
import csv
import os
import sqlite3

import aiosqlite
import cassiopeia as cass
from api_client import RiotAPI
from cassiopeia import MatchHistory, Queue, Summoner
from common import get_summoner_details, update_summoner_details_in_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# create API client
api_client = RiotAPI(RIOT_API_KEY)

# use client
summoner_name = "gameb0x"
region = "NA"
summoner = api_client.find_player_by_name(summoner_name, region)


# Connect to SQLite database (or create it if it doesn't exist)
with sqlite3.connect("lol_summoner.db") as conn:
    cursor = conn.cursor()
    cursor.execute(
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
    cursor.execute(
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
    cursor.execute(
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
        win BOOLEAN NOT NULL
    )
    """
    )
    conn.commit()


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
                region TEXT NOT NULL,
                game_creation INTEGER NOT NULL,
                game_duraion INTEGER NOT NULL,
                champion_name TEXT NOT NULL,
                role TEXT NOT NULL,
                kills INTEGER NOT NULL,
                deaths INTEGER NOT NULL,
                assists INTEGER NOT NULL,
                total_damage_dealt_to_champions INTEGER NOT NULL,
                vision_score INTEGER NOT NULL,
                gold_earned INTEGER NOT NULL,
                total_minions_killed INTEGER NOT NULL,
                win BOOLEAN NOT NULL,
                FOREIGN KEY(puuid) REFERENCES top_champion_players(puuid),
                UNIQUE(match_id)
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
                    row["Summoner"], row["Region"]
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


async def fetch_summoner_details(summoner_name: str, region: str):
    summoner = cass.get_summoner(name=summoner_name)
    puuid = summoner.puuid
    account_id = summoner.account_id
    profile_icon_id = summoner.profile_icon.id
    return puuid, account_id, profile_icon_id


# Function to retrieve and update summoner details
def update_summoner_details():
    with sqlite3.connect("lol_summoner.db") as conn:
        cursor = conn.cursor()
        summoners = cursor.execute(
            "SELECT summoner_name, region FROM top_champion_players"
        ).fetchall()
        for summoner_name, region in summoners:
            summoner = cass.get_summoner(name=summoner_name, region=region)
            cursor.execute(
                """
                UPDATE top_champion_players
                SET accountId = ?, puuid = ?, profileIconID = ?
                WHERE summoner_name = ? AND region = ?
                """,
                (
                    summoner.account_id,
                    summoner.puuid,
                    summoner.profile_icon.id,
                    summoner_name,
                    region,
                ),
            )
        conn.commit()


# Function to fetch and store match history
async def fetch_and_store_match_history(summoner_name: str, region: str):
    # Connect to the database
    conn = sqlite3.connect("lol_summoner.db")
    cursor = conn.cursor()

    # Fetch the summoner's match history
    summoner = cass.get_summoner(name=summoner_name, region=region)
    match_history = summoner.match_history

    for match in match_history:
        # Extract relevant data from the match
        participant = match.participants[summoner]
        match_data = (
            match.id,
            participant.champion.name,
            match.creation.timestamp(),
            match.duration.seconds,
            participant.stats.win,
            participant.stats.kills,
            participant.stats.deaths,
            participant.stats.assists,
            participant.stats.total_damage_dealt_to_champions,
            participant.stats.vision_score,
            participant.stats.gold_earned,
            participant.stats.total_minions_killed,
        )

        # Insert the match data into the database
        cursor.execute(
            """
        INSERT INTO match_history (summoner_name, region, match_id, champion_name, game_creation, game_duration, win, kills, deaths, assists, total_damage_dealt_to_champions, vision_score, gold_earned, total_minions_killed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            match_data,
        )

    # Commit the changes and close the connection
    conn.commit()


# Main function
if __name__ == "__main__":
    asyncio.run(fetch_and_store_match_history(summoner_name, region))
    update_summoner_details()

# Close the connection
conn.close()
