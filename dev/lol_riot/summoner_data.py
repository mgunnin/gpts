from fastapi import APIRouter, HTTPException
from models import Summoner
from database import Database
from riot_api_wrapper import RiotAPIWrapper

router = APIRouter()
db = Database()
api_wrapper = RiotAPIWrapper()


@router.get("/summoner/{region}/{summoner_name}", response_model=Summoner)
async def get_summoner_data(region: str, summoner_name: str):
    """
    Endpoint to retrieve summoner data by name and region.
    """
    # Fetch summoner data from Riot API
    try:
        summoner_data = api_wrapper.get_summoner_by_name(region, summoner_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Summoner data not found: {e}")

    # Check if summoner data already exists in the database
    existing_summoner = db.execute_query(
        "SELECT * FROM summoners WHERE summoner_name = %s AND region = %s",
        (summoner_name, region),
        fetch=True,
    )

    # If not, insert the new summoner data into the database
    if not existing_summoner:
        db.execute_query(
            """
            INSERT INTO summoners (summoner_name, region, profile_icon_id, summoner_level)
            VALUES (%s, %s, %s, %s)
            """,
            (
                summoner_name,
                region,
                summoner_data.get("profileIconId"),
                summoner_data.get("summonerLevel"),
            ),
        )

    # Return the summoner data
    return Summoner(
        summoner_name=summoner_name,
        region=region,
        profile_icon_id=summoner_data.get("profileIconId"),
        summoner_level=summoner_data.get("summonerLevel"),
    )
