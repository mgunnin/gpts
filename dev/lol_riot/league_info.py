from fastapi import APIRouter, HTTPException
from models import LeagueInfo
from riot_api_wrapper import RiotAPIWrapper
from database import Database

router = APIRouter()
riot_api_wrapper = RiotAPIWrapper()
db = Database()


@router.get("/league-info/{region}/{summoner_name}", response_model=LeagueInfo)
async def get_league_info(region: str, summoner_name: str):
    """
    Endpoint to fetch league information for a given summoner.
    """
    try:
        # Fetch summoner details to get the summoner ID
        summoner_details = riot_api_wrapper.get_summoner_by_name(region, summoner_name)
        if not summoner_details:
            raise HTTPException(status_code=404, detail="Summoner not found")

        summoner_id = summoner_details["id"]

        # Fetch league information using the summoner ID
        league_info = riot_api_wrapper.get_league_info(region, summoner_id)
        if not league_info:
            raise HTTPException(status_code=404, detail="League information not found")

        # Transform the API response into our LeagueInfo model
        league_info_models = [LeagueInfo(**info) for info in league_info]

        # Store or update league information in the database
        for info in league_info_models:
            db.execute_query(
                """
                INSERT INTO league_info (summoner_id, queue_type, rank, tier, league_points, wins, losses)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (summoner_id, queue_type) DO UPDATE
                SET rank = EXCLUDED.rank, tier = EXCLUDED.tier, league_points = EXCLUDED.league_points, wins = EXCLUDED.wins, losses = EXCLUDED.losses;
            """,
                (
                    info.summoner_id,
                    info.queue_type,
                    info.rank,
                    info.tier,
                    info.league_points,
                    info.wins,
                    info.losses,
                ),
            )

        return league_info_models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
