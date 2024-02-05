import asyncio
import csv

import cassiopeia as cass
from cassiopeia import Queue
from config import CONFIG
from database import insert_top_champion_players

cass.set_riot_api_key(CONFIG["RIOT_API_KEY"])


async def fetch_and_store_player_data(summoner_name, region):
    try:
        summoner = cass.get_summoner(name=summoner_name, region=region)
        if hasattr(summoner, "puuid") and summoner.puuid:
            player_data = {
                "summoner_name": summoner.name,
                "region": region,
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
                    player_data["puuid"],
                    player_data["account_id"],
                    player_data["profile_icon_id"],
                    player_data["summoner_level"],
                    player_data["summoner_id"],
                )
            )
        else:
            print(f"Summoner {summoner_name} in region {region} does not have a puuid.")
    except Exception as e:
        print(f"An error occurred while processing {summoner_name}: {str(e)}")


async def process_csv_file(file_path):
    tasks = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            _, region, _, _, summoner_name = row
            task = fetch_and_store_player_data(summoner_name, region)
            tasks.append(task)
    await asyncio.gather(*tasks)


async def fetch_match_history(puuid: str, region):
    summoner = cass.get_summoner(name=puuid, region=region)
    match_history = cass.get_match_history(
        continent=region, puuid=puuid, queue=Queue.ranked_solo_fives, count=20
    )
    matches_data = []
    for match in match_history:
        match_data = (
            region,
            match.game_id,
            match.id,
            match.participants[summoner].champion.name,
            match.participants[summoner].stats.kills,
            match.participants[summoner].stats.deaths,
            match.participants[summoner].stats.assists,
            match.participants[summoner].stats.total_damage_dealt_to_champions,
            match.participants[summoner].stats.vision_score,
            match.participants[summoner].stats.gold_earned,
            match.participants[summoner].stats.total_minions_killed,
            match.participants[summoner].role,
            match.participants[summoner].stats.win,
        )
        matches_data.append(match_data)
    return matches_data
