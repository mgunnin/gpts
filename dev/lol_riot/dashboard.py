from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from models import Summoner, ChampionMastery, LeagueInfo, MatchData
from database import Database
from riot_api_wrapper import RiotAPIWrapper
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Assuming the static files (CSS, JS, images) are stored in a directory named 'static'
router.mount("/static", StaticFiles(directory="static"), name="static")

db = Database()
api_wrapper = RiotAPIWrapper()


@router.get("/dashboard/{region}/{summoner_name}", response_class=HTMLResponse)
async def get_dashboard(region: str, summoner_name: str):
    """
    Endpoint to display the dashboard for a given summoner.
    """
    try:
        # Fetch summoner data
        summoner_data = api_wrapper.get_summoner_by_name(region, summoner_name)
        if not summoner_data:
            raise HTTPException(status_code=404, detail="Summoner not found")

        # Fetch champion mastery data
        champion_mastery_data: List[ChampionMastery] = api_wrapper.get_champion_mastery(
            region, summoner_data["id"]
        )

        # Fetch league info
        league_info_data: LeagueInfo = api_wrapper.get_league_info(
            region, summoner_data["id"]
        )

        # Fetch recent match data - assuming a method exists to fetch the latest matches
        recent_matches: List[MatchData] = api_wrapper.get_recent_matches(
            region, summoner_data["id"]
        )

        # Prepare data for rendering
        data = {
            "summoner": summoner_data,
            "champion_mastery": champion_mastery_data,
            "league_info": league_info_data,
            "recent_matches": recent_matches,
        }

        # Render the dashboard template with the fetched data
        return templates.TemplateResponse(
            "dashboard.html", {"request": request, "data": data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
