import logging
import os

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from constants import REGIONS
from database_pg import Database, ProcessPerformance
from extract_pg import main as extract_main
from riot_api import RiotAPI

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Esports Playmaker",
    description="A FastAPI application for the Esports Playmaker plugin.",
    version="0.1.0",
    servers=[
        {"url": "http://127.0.0.1:8000/"},
        {"url": "https://lacralabs.replit.app"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database(os.getenv("DATABASE_URL")).get_connection()


# API endpoints
@app.on_event("startup")
async def startup_event():
    global riot_api
    riot_api = RiotAPI(db)


@app.get("/summoner/{summoner_name}")
async def get_summoner_info(summoner_name: str, region: str = "na1"):
    """
    Retrieves summoner information based on the summoner name and region.

    Args:
        summoner_name (str): The summoner name.
        region (str, optional): The region of the summoner. Defaults to "na1".

    Returns:
        dict: The summoner information.
    """
    if region not in REGIONS:
        return {"error": "Invalid region"}
    try:
        summoner_info = riot_api.summoner_info(summoner_name, region)
        return summoner_info
    except Exception as e:
        return {"error": f"Error retrieving summoner information: {e}"}


@app.get("/champion_mastery/{puuid}")
async def get_champion_mastery(puuid: str, region: str = "na1"):
    """
    Retrieves the champion mastery for a given player.

    Args:
        puuid (str): The unique identifier for the player.
        region (str, optional): The region where the player is located. Defaults to "na1".

    Returns:
        dict: A dictionary containing the champion mastery information, or an error message if an exception occurs.
    """
    try:
        riot_api = RiotAPI(db)
        champion_mastery = riot_api.champion_mastery(puuid, region)
        return champion_mastery
    except Exception as e:
        return {"error": f"Error retrieving champion mastery: {e}"}


@app.get("/champion_mastery/scores/{puuid}")
async def get_champion_mastery_top_score(puuid: str, region: str = "na1"):
    """
    Retrieves the total champion mastery score for a given player.

    Args:
        puuid (str): The player's unique identifier.
        region (str, optional): The region where the player is located. Defaults to "na1".

    Returns:
        dict: A dictionary containing the total champion mastery score, or an error message if an exception occurs.
    """
    try:
        riot_api = RiotAPI(db)
        champion_mastery_score = riot_api.champion_mastery_total_score(puuid, region)
        return champion_mastery_score
    except Exception as e:
        return {"error": f"Error retrieving total champion mastery score: {e}"}


@app.get("/summoner/leagues/{summonerId}")
async def get_summoner_leagues(summonerId: str, region: str = "na1"):
    """
    Retrieves a list of league information for the given summoner ID.

    Args:
        summonerId (str): The summoner ID.
        region (str, optional): The region of the summoner. Defaults to "na1".

    Returns:
        dict: A dictionary containing the league information for the given summoner ID.
    """
    try:
        riot_api = RiotAPI(db)
        summoner_leagues = riot_api.summoner_leagues(summonerId, region)
        return summoner_leagues
    except Exception as e:
        return {"error": f"Error retrieving summoner leagues: {e}"}


@app.get("/summoner/match_list/{puuid}")
async def get_match_list(
    puuid: str,
    num_matches: int = 10,
    queue_type: str = "ranked",
    region: str = "americas",
):
    """
    Retrieves a list of match IDs based on the player UUID, number of matches, queue type, and region.
    """
    logging.info(
        f"Fetching match list for PUUID: {puuid}, Num Matches: {num_matches}, Queue Type: {queue_type}, Region: {region}"
    )
    try:
        riot_api = RiotAPI(db)
        match_list = riot_api.match_ids(puuid, num_matches, queue_type, region)
        if not match_list:
            logging.warning("Received empty match list.")
        return match_list
    except Exception as e:
        logging.error(f"Error retrieving match list: {e}")
        return {"error": f"Error retrieving match list: {e}"}


@app.get("/match_detail/{match_id}")
async def get_match_detail(match_id: str, db):
    """
    Retrieves the match detail for a given match ID.
    """
    try:
        match_detail = (
            db.cursor()
            .execute("SELECT * FROM match_detail WHERE match_id = ?", (match_id,))
            .fetchone()
        )
        if match_detail is not None:
            return match_detail
        else:
            return {"error": "Match not found"}
    except Exception as e:
        return {"error": f"Error retrieving match detail: {e}"}


@app.post("/performance")
async def calculate_performance(match_id: str):
    """
    Calculates player performance based on match details.

    Args:
        match_id (str): The match ID.
        db: The database connection.

    Returns:
        dict: The calculated performance data.
    """
    try:
        match_detail = db.cursor().execute(
            "SELECT * FROM match_detail WHERE match_id = ?", (match_id,)
        )
        if match_detail:
            performance_calculator = ProcessPerformance(db)
            performance_data = performance_calculator.process_player_performance(
                match_detail[0], db
            )
            return performance_data
        else:
            return {"error": "Match not found"}
    except Exception as e:
        return {"error": f"Error calculating performance: {e}"}


@app.post("/data_mining/{mode}")
async def data_mining(mode: str, background_tasks: BackgroundTasks):
    valid_modes = [
        "player_list",
        "match_list",
        "match_download_standard",
        "match_download_detail",
    ]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail="Invalid mode specified")

    # Use BackgroundTasks to run the data mining process without blocking the API response
    background_tasks.add_task(extract_main, mode)
    return {"message": "Data mining process initiated", "mode": mode}


@app.get("/")
async def home():
    return {"message": "Welcome to the Esports Playmaker"}


@app.get("/public/logo.png")
async def plugin_logo():
    return FileResponse("logo.png", media_type="image/png")


@app.get("/public/favicon.ico")
async def plugin_favicon():
    return FileResponse("favicon.ico", media_type="image/x-icon")


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
    uvicorn.run(app, host="0.0.0.0", port=8080)
