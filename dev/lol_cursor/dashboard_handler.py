from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from champion_mastery import get_champion_mastery
from database.database import get_db
from league_info import get_league_info
from match_data import MatchDataHandler
from player_performance import PlayerPerformance
from summoner_data import get_summoner_data

app = FastAPI()


def generate_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>League of Legends Dashboard</title>
            <link rel="stylesheet" type="text/css" href="style.css">
        </head>
        <body>
            <h1>League of Legends Performance Dashboard</h1>
            <div id="summonerProfile"></div>
            <div id="masteryStats"></div>
            <div id="leagueInfo"></div>
            <div id="matchHistory"></div>
            <div id="performanceMetrics"></div>
            <script src="script.js"></script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html = generate_dashboard()
    return html


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that accepts a connection and listens for incoming text data.
    When data is received, it splits the data into a summoner name and region.
    It then uses several functions to retrieve and process summoner data, champion mastery stats,
    league info, match history, and performance metrics.
    The results are sent back to the client as a JSON object.
    """
    await websocket.accept()

    async for data in websocket.iter_text():
        summoner_name, region = data.split(",")
        db: AsyncSession = Depends(get_db)

        try:
            summoner_profile = await get_summoner_data(region, summoner_name, db)
            mastery_stats = await get_champion_mastery(summoner_name, region, db)
            league_info = await get_league_info(summoner_name, region, db)

            match_data_handler = MatchDataHandler()
            match_history = await match_data_handler.fetch_match_data(region, summoner_profile["puuid"])

            performance_metrics = PlayerPerformance()
            performance_metrics.calculate_performance_metrics()

            await websocket.send_json({
                "summonerProfile": summoner_profile,
                "masteryStats": mastery_stats,
                "leagueInfo": league_info,
                "matchHistory": match_history,
                "performanceMetrics": performance_metrics,
            })
        except HTTPException as e:
            await websocket.send_text(f"Error: {e.detail}")
