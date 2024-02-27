import os

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from database_pg import Database, ProcessPerformance
from exceptions import MissingEnvironmentVariableError
from riot_api import RiotAPI

ORIGINS = os.getenv("ORIGINS")
if not ORIGINS:
    raise MissingEnvironmentVariableError("ORIGINS")

origins = ORIGINS.split(",")

app = FastAPI()
db = Database.get_connection

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Trigger the background task on startup
async def populate_database():
    """
    Background task that populates the database with top players' information.
    """
    riot_api = RiotAPI(db)
    for region in riot_api.request_regions:
        for queue in ["RANKED_SOLO_5x5"]:
            riot_api.get_top_players(region, queue, db)

async def lifespan():
    """
    Lifespan event handler that adds the background task to populate the database.
    """
    background_tasks = BackgroundTasks()
    background_tasks.add_task(populate_database)


# API endpoints
@app.get("/summoner/{summoner_name}")
async def get_summoner_information(summoner_name: str, region: str = "na1"):
    """
    Retrieves summoner information based on the summoner name and region.

    Args:
        summoner_name (str): The summoner name.
        region (str, optional): The region of the summoner. Defaults to "na1".

    Returns:
        dict: The summoner information.
    """
    try:
        riot_api = RiotAPI(db)
        summoner_info = riot_api.get_summoner_information(summoner_name, region)
        return summoner_info
    except Exception as e:
        return {"error": f"Error retrieving summoner information: {e}"}

@app.get("/champion_mastery/{puuid}")
async def get_champion_mastery(puuid: str, region: str = "na1"):
    """
    Retrieves champion mastery information based on the player UUID and region.

    Args:
        puuid (str): The player UUID.
        region (str, optional): The region of the player. Defaults to "na1".

    Returns:
        dict: The champion mastery information.
    """
    try:
        riot_api = RiotAPI(db)
        champion_mastery = riot_api.get_champion_mastery(puuid, region)
        return champion_mastery
    except Exception as e:
        return {"error": f"Error retrieving champion mastery: {e}"}


@app.get("/champion_mastery/scores/{puuid}")
async def get_total_champion_mastery_score(puuid: str, region: str = "na1"):
    try:
        riot_api = RiotAPI(db)
        total_champion_mastery_score = riot_api.get_total_champion_mastery_score(puuid, region)
        return total_champion_mastery_score
    except Exception as e:
        return {"error": f"Error retrieving total champion mastery score: {e}"}


@app.get("/summoner/leagues/{summonerId}")
async def get_summoner_leagues(summonerId: str, region: str = "na1"):
    try:
        riot_api = RiotAPI(db)
        summoner_leagues = riot_api.get_summoner_leagues(summonerId, region)
        return summoner_leagues
    except Exception as e:
        return {"error": f"Error retrieving summoner leagues: {e}"}



@app.get("/match_list/{puuid}")
async def get_match_list(puuid: str, num_matches: int = 10, queue_type: str = "ranked", region: str = "americas"):
    """
    Retrieves a list of match IDs based on the player UUID, number of matches, queue type, and region.

    Args:
        puuid (str): The player UUID.
        num_matches (int, optional): The number of matches to retrieve. Defaults to 10.
        queue_type (str, optional): The type of queue. Defaults to "ranked".
        region (str, optional): The region of the player. Defaults to "americas".

    Returns:
        dict: The list of match IDs.
    """
    try:
        riot_api = RiotAPI(db)
        match_list = riot_api.get_match_ids(puuid, num_matches, queue_type, region)
        return match_list
    except Exception as e:
        return {"error": f"Error retrieving match list: {e}"}


@app.get("/match_detail/{match_id}")
async def get_match_detail(match_id: str):
    """
    Retrieves detailed match information from the database based on the match ID.

    Args:
        match_id (str): The match ID.

    Returns:
        dict: The detailed match information.
    """
    try:
        match_detail = db.execute("SELECT * FROM match_detail WHERE match_id = ?", (match_id,)).fetchone()
        return match_detail
    except Exception as e:
        return {"error": f"Error retrieving match detail: {e}"}


@app.post("/performance")
async def calculate_performance(match_id: str):
    """
    Calculates player performance based on match details.

    Args:
        match_id (str): The match ID.

    Returns:
        dict: The calculated performance data.
    """
    try:
        match_detail = db.execute("SELECT * FROM match_detail WHERE match_id = ?", (match_id,)).fetchone()
        if match_detail:
            performance_calculator = ProcessPerformance(db)
            performance_data = performance_calculator.process_player_performance(match_detail[0], db.get_connection())
            return performance_data
        else:
            return {"error": "Match not found"}
    except Exception as e:
        return {"error": f"Error calculating performance: {e}"}


@app.get("/")
def home():
  return {"message": "Welcome to the Esports Playmaker"}


@app.get("/logo.png")
async def plugin_logo():
  return FileResponse("logo.png", media_type="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
  with open("ai-plugin.json", "r") as f:
    json_content = f.read()
  return Response(content=json_content, media_type="application/json")


@app.get("/openapi.yaml")
async def openapi_spec(request: Request):
  host = request.client.host if request.client else "localhost"
  with open("openapi.yaml", "r") as f:
    yaml_content = f.read()
  yaml_content = yaml_content.replace("PLUGIN_HOSTNAME", f"https://{host}")
  return Response(content=yaml_content, media_type="application/yaml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
