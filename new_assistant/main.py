import asyncio

from database import create_db, fetch_all_puuids, insert_match_history
from riot_api import fetch_match_history_by_puuid, process_csv_file


async def main():
    await create_db()
    await process_csv_file("../data/lol/lol_champion_player_ranks_testing.csv")
    puuids = await fetch_all_puuids()
    for puuid in puuids:
        matches_data = await fetch_match_history_by_puuid(puuid, continent="AMERICAS")
        for match_data in matches_data:
            await insert_match_history(match_data)


if __name__ == "__main__":
    asyncio.run(main())
