import asyncio
import csv
import traceback

import cassiopeia as cass
from cassiopeia import Queue
from config import CONFIG
from database import insert_top_champion_players, puuid_exists

cass.set_riot_api_key(CONFIG["RIOT_API_KEY"])


async def fetch_and_store_player_data(summoner_name, region, champion):
    """
    Asynchronously fetches and stores player data for a given summoner name, region, and champion.

    This function performs several key operations to ensure that the player data related to a specific summoner name,
    region, and champion is fetched from the Riot Games API and stored in the database efficiently and correctly. The
    process involves fetching the summoner's details using the Cassiopeia wrapper for the Riot Games API, checking if
    the player's unique identifier (puuid) already exists in the database to avoid duplicate entries, and inserting the
    player's data into the database if it is new.

    The function handles exceptions gracefully, printing out the error details and a traceback for debugging purposes
    if an error occurs during the process. It ensures that only unique player data is stored in the database by checking
    the presence of the summoner's puuid in the database before attempting to insert new data.

    Parameters:
    - summoner_name (str): The name of the summoner whose data is to be fetched and stored.
    - region (str): The region in which the summoner plays (e.g., 'NA', 'EUW', etc.).
    - champion (str): The name of the champion for which the player data is being fetched.

    Returns:
    - None: This function does not return any value. It performs database operations and prints messages to the console.

    Raises:
    - Exception: Catches and handles any exceptions that occur during the execution of the function, printing the error
      type, message, and a traceback for debugging purposes.
    """
    try:
        summoner = cass.get_summoner(name=summoner_name, region=region)
        if hasattr(summoner, "puuid") and summoner.puuid:
            # Check if the puuid already exists in the database to avoid duplicates
            if not await puuid_exists(summoner.puuid):
                player_data = {
                    "summoner_name": summoner.name,
                    "region": region,
                    "champion": champion,
                    "puuid": summoner.puuid,
                    "account_id": summoner.account_id,
                    "profile_icon_id": summoner.profile_icon.id,
                    "summoner_level": summoner.level,
                    "summoner_id": summoner.id,
                }
                await insert_top_champion_players(
                    (
                        player_data["summoner_name"],
                        player_data["region"],
                        player_data["champion"],
                        player_data["puuid"],
                        player_data["account_id"],
                        player_data["profile_icon_id"],
                        player_data["summoner_level"],
                        player_data["summoner_id"],
                    )
                )
            else:
                print(
                    f"Summoner {summoner_name} with puuid {summoner.puuid} already exists in the database."
                )
        else:
            print(f"Summoner {summoner_name} in region {region} does not have a puuid.")
    except Exception as e:
        print(
            f"An error of type {type(e).__name__} occurred while processing {summoner_name}: {str(e)}"
        )
        traceback.print_exc()


async def process_csv_file(file_path):
    unique_summoners = set()
    tasks = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            champion, region, _, _, summoner_name = row
            if summoner_name not in unique_summoners:
                unique_summoners.add(summoner_name)
                task = fetch_and_store_player_data(summoner_name, region, champion)
                tasks.append(task)
    await asyncio.gather(*tasks)


async def fetch_match_history_by_puuid(puuid: str, continent):
    """
    Fetches the match history for a given player's PUUID and a specific continent.

    This function retrieves the match history of a player identified by their PUUID (Player Universally Unique Identifier)
    on a specified continent. It queries the match history using the Cassiopeia library, filtering for ranked solo 5v5 games
    and limiting the results to the 10 most recent matches. For each match in the history, it extracts detailed information
    about the player's performance, including game ID, PUUID, summoner name, champion played, kills, deaths, assists, KDA ratio,
    total damage dealt, total damage taken, total healing done, total damage dealt to champions, total minions killed, vision score,
    gold earned, and whether the match was won or lost.

    The function returns a list of dictionaries, each representing the data for one match.

    Parameters:
    - puuid (str): The PUUID of the player whose match history is being fetched.
    - continent (str): The continent on which the player's match history is to be queried.

    Returns:
    - list[dict]: A list of dictionaries, each containing detailed information about a single match from the player's history.
    """
    match_history = cass.get_match_history(
        continent=continent,
        puuid=puuid,
        queue=Queue.ranked_solo_fives,
        count=10,
    )
    matches_data = []
    for match in match_history:
        summoner = match.participants[puuid]
        match_data = {
            "game_id": match.id,
            "puuid": puuid,
            "summoner_name": summoner.summoner.name,
            "champion_name": summoner.champion.name,
            "kills": summoner.stats.kills,
            "deaths": summoner.stats.deaths,
            "assists": summoner.stats.assists,
            "kda": summoner.stats.kda,
            "total_damage_dealt": summoner.stats.total_damage_dealt,
            "total_damage_taken": summoner.stats.total_damage_taken,
            "total_healing_done": summoner.stats.total_heal,
            "total_damage_dealt_to_champions": summoner.stats.total_damage_dealt_to_champions,
            "total_minions_killed": summoner.stats.total_minions_killed,
            "vision_score": summoner.stats.vision_score,
            "gold_earned": summoner.stats.gold_earned,
            "win": summoner.stats.win,
        }
        matches_data.append(match_data)
    return matches_data
