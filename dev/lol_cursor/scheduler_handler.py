import asyncio
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data_population import fetch_top_players
from riot_api_wrapper import RiotAPIWrapper

# Configuration for the scheduler
SCHEDULE_INTERVAL_HOURS = 24  # How often to refresh data, set to every 24 hours

# Initialize the Riot API Wrapper with your API key
api_key = os.environ.get("RIOT_API_KEY")
if api_key is None:
    raise ValueError("API key is required")
riot_api = RiotAPIWrapper(api_key)

# Regions to update data for
REGIONS = ["NA1", "EUW1", "EUN1", "KR"]


def start_background_tasks():
    """
    This function schedules the background tasks for fetching and updating top player data.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_top_players_data,
        "interval",
        hours=SCHEDULE_INTERVAL_HOURS,
        next_run_time=None,
    )
    scheduler.start()


async def update_top_players_data():
    """
    This coroutine fetches and updates the top players' data for each region.
    """
    for region in REGIONS:
        await fetch_top_players(riot_api, region)
    print("Top players data updated successfully.")


if __name__ == "__main__":
    # Start the background tasks for updating data
    start_background_tasks()

    # Run the main event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
