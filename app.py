from fastapi import BackgroundTasks

from database_pg import Database
from riot_api import RiotAPI

db = Database.get_connection


# Trigger the background task on startup
async def populate_database():
    """
    Background task that populates the database with top players' information.
    """
    riot_api = RiotAPI(db)
    for region in riot_api.regions:
        for queue in ["RANKED_SOLO_5x5"]:
            riot_api.top_players(region, queue, db)


async def lifespan():
    """
    Lifespan event handler that adds the background task to populate the database.
    """
    background_tasks = BackgroundTasks()
    background_tasks.add_task(populate_database)
