from fastapi import APIRouter, HTTPException
from models import ChampionMastery
from database import Database
from riot_api_wrapper import RiotAPIWrapper

router = APIRouter()
db = Database()
riot_api = RiotAPIWrapper()


@router.get(
    "/champion-mastery/{region}/{summoner_name}", response_model=list[ChampionMastery]
)
async def get_champion_mastery(region: str, summoner_name: str):
    """
    Fetch and return champion mastery details for a given summoner name and region.
    """
    # Connect to the database
    db.connect()

    # Fetch summoner details from Riot API
    summoner = riot_api.get_summoner_by_name(region, summoner_name)
    if not summoner:
        raise HTTPException(status_code=404, detail="Summoner not found")

    # Fetch champion mastery details for the summoner
    mastery_details = riot_api.get_champion_mastery(region, summoner["id"])
    if not mastery_details:
        raise HTTPException(
            status_code=404, detail="Champion mastery details not found"
        )

    # Prepare and execute the query to insert or update champion mastery details in the database
    for mastery in mastery_details:
        query = """
        INSERT INTO champion_mastery (summoner_id, champion_id, mastery_level, mastery_points)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (summoner_id, champion_id) DO UPDATE
        SET mastery_level = EXCLUDED.mastery_level, mastery_points = EXCLUDED.mastery_points;
        """
        params = (
            summoner["id"],
            mastery["championId"],
            mastery["championLevel"],
            mastery["championPoints"],
        )
        db.execute_query(query, params)

    # Convert the API response to ChampionMastery models
    champion_masteries = [
        ChampionMastery(
            **{
                "summoner_id": summoner["id"],
                "champion_id": mastery["championId"],
                "mastery_level": mastery.get("championLevel"),
                "mastery_points": mastery.get("championPoints"),
            }
        )
        for mastery in mastery_details
    ]

    return champion_masteries
