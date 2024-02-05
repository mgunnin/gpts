import asyncio
import csv
import traceback

import arrow
import cassiopeia as cass
from cassiopeia import Queue
from config import CONFIG
from database import insert_top_champion_players, puuid_exists

cass.set_riot_api_key(CONFIG["RIOT_API_KEY"])


async def fetch_and_store_player_data(summoner_name, region, champion):
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
    # Directly use PUUID to fetch match history
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
            "game_duration": match.duration,
            "puuid": puuid,
            "summoner_name": summoner.summoner.name,
            "champion_name": summoner.champion.name,
            "kills": summoner.stats.kills,
            "deaths": summoner.stats.deaths,
            "assists": summoner.stats.assists,
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
