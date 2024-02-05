import asyncio

from database import create_db, fetch_all_puuids, insert_match_history
from riot_api import fetch_match_history, process_csv_file


async def main():
    await create_db()
    # Process the CSV file to fetch and store player data
    await process_csv_file("lol_champion_player_ranks_testing.csv")
    puuids = await fetch_all_puuids()
    for puuid in puuids:
        matches_data = await fetch_match_history(puuid, continent="AMERICAS")
        for match_data in matches_data:
            await insert_match_history(match_data)


if __name__ == "__main__":
    asyncio.run(main())
