import asyncio
import csv
import logging
import os
import sqlite3

import aiosqlite
import requests
from dotenv import load_dotenv

from models import MassRegion, Region
from utils import get_api_response

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
RIOT_API_BASE_URL = os.getenv("RIOT_API_BASE_URL")

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("lol_summoner.db")
cursor = conn.cursor()

# Create table to store top player data for each champion
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS top_champion_players (
        champion TEXT NOT NULL,
        region TEXT NOT NULL,
        rank INTEGER NOT NULL,
        tier TEXT NOT NULL,
        summoner_name TEXT NOT NULL,
        puuid TEXT UNIQUE NOT NULL,
        PRIMARY KEY (champion, summoner_name, rank)
    )
    """
)

# Commit the changes
conn.commit()


# Function to load data from CSV into the database
def load_top_players_data(csv_file_path):
    with open(csv_file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute(
                """
                INSERT OR REPLACE INTO top_champion_players (champion, region, rank, tier, summoner_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row["Champion"],
                    row["Region"],
                    row["Rank"],
                    row["Tier"],
                    row["Summoner"],
                ),
            )
    # Commit the changes
    conn.commit()


# Load data from CSV file
load_top_players_data("datasets/lol_champion_player_ranks_1-5.csv")

# Create table to store summoners
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS summoners (
        summoner_name TEXT NOT NULL,
        region TEXT NOT NULL,
        puuid TEXT NOT NULL,
        riot_id TEXT NOT NULL,
        PRIMARY KEY (summoner_name, region)
    )
    """
)
conn.commit()


# Create table to store match statistics
cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS match_statistics (
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
        PRIMARY KEY (puuid, match_id)
    )
    """
)
conn.commit()


async def fetch_puuid(summoner_name: str, region: Region):
    url = f"https://{region.value}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response, status_code = await get_api_response(url, headers)
    return response.get("puuid", ""), status_code


async def fetch_and_store_summoner_data():
    with open("datasets/lol_champion_player_ranks_1-5.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            puuid = await fetch_puuid(row["Summoner"], row["Region"])
            if puuid:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO top_champion_players (champion, region, rank, tier, summoner_name, puuid)
                    VALUES (?, ?, ?, ?, ?, ?)
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
                conn.commit()


async def fetch_and_store_match_statistics(puuid):
    url = f"{RIOT_API_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        match_ids = response.json()
        for match_id in match_ids:
            match_data, status_code = await get_api_response(
                f"{RIOT_API_BASE_URL}/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
            )
            if status_code == 200:
                for participant in match_data["info"]["participants"]:
                    if participant["puuid"] == puuid:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO match_statistics (puuid, match_id, game_creation, champion_name, kills, deaths, assists, total_damage_dealt_to_champions, vision_score, gold_earned, total_minions_killed, role, win)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                puuid,
                                match_id,
                                match_data["info"]["gameCreation"],
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
                        conn.commit()


async def fetch_and_store_detailed_summoner_matches(
    summoner_name,
    region: Region = Region.na1,
    mass_region: MassRegion = MassRegion.americas,
):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with aiosqlite.connect("lol_summoner.db") as db:
        db_cursor = await db.cursor()

        # Fetch PUUID and Riot ID for the summoner
        summoner_response, status_code = await get_api_response(
            f"https://{region.value}.{RIOT_API_BASE_URL}/lol/summoner/v4/summoners/by-name/{summoner_name}",
            headers,
        )

        # Check if the summoner was found
        if status_code == 404:
            logging.error(f"Summoner {summoner_name} not found, skipping.")
            return
        elif status_code != 200:
            logging.error(
                f"Error retrieving summoner {summoner_name}: {summoner_response.get('status', {}).get('message', '')}"
            )
            return

        # Extract the actual summoner name and PUUID from the response
        summoner_name = summoner_response["name"]
        puuid = summoner_response["puuid"]

        # Store the summoner data in the database
        await db_cursor.execute(
            """
            INSERT OR IGNORE INTO summoners (
                summoner_name,
                region,
                puuid
            ) VALUES (?, ?, ?)
            """,
            (summoner_name, region.value, puuid),
        )

        # Fetch match IDs for the summoner using PUUID
        match_ids_response, match_ids_status = await get_api_response(
            f"https://{mass_region.value}.{RIOT_API_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20",
            headers,
        )

        if match_ids_status != 200:
            logging.error(
                f"Error retrieving match IDs for summoner {summoner_name}: {match_ids_response.get('status', {}).get('message', '')}"
            )
            return

        # Fetch and store data for each match using match IDs
        for match_id in match_ids_response:
            match_data_response, match_data_status = await get_api_response(
                f"https://{mass_region.value}.{RIOT_API_BASE_URL}/lol/match/v5/matches/{match_id}",
                headers,
            )

            if match_data_status != 200:
                logging.error(
                    f"Error retrieving match data for match ID {match_id}: {match_data_response.get('status', {}).get('message', '')}"
                )
                continue

            # Extract match details and store them in the database
            match_info = match_data_response["info"]
            for participant in match_info["participants"]:
                if participant["puuid"] == puuid:
                    await db_cursor.execute(
                        """
                        INSERT OR IGNORE INTO detailed_summoner_match_data (
                            summoner_id,
                            match_id,
                            timestamp,
                            champion,
                            kills,
                            deaths,
                            assists,
                            total_damage_dealt_to_champions,
                            vision_score,
                            gold_earned,
                            total_minions_killed,
                            role,
                            win
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            summoner_name,
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


# Main execution block
if __name__ == "__main__":
    asyncio.run(fetch_and_store_summoner_data())
    summoners = cursor.execute("SELECT puuid FROM summoners").fetchall()
    for summoner in summoners:
        asyncio.run(fetch_and_store_match_statistics(summoner[0]))
    conn.close()
