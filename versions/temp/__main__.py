from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from temp.helpers import get_summoner_info, get_match_ids_by_puuid, get_match_by_id, get_match_timeline_by_id

app = FastAPI()

# Set up CORS middleware
origins = [
    "http://localhost:8000",
    "https://lacra-gpt-lol.replit.app/",
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/summoner/{summoner_name}")
async def get_summoner(summoner_name: str, region: str = "na1"):
    """
    Get summoner by name

    Args:
        summoner_name (str): Summoner name
        region (str): Region

    Returns:
        dict: Summoner data
    """
    return await get_summoner_info(summoner_name, region)

@app.get("/summoner/{summoner_name}/matches")
async def get_summoner_matches(summoner_name: str, region: str = "na1"):
    """
    Get summoner matches by name

    Args:
        summoner_name (str): Summoner name
        region (str): Region

    Returns:
        list: Match ids
    """
    summoner = await get_summoner_info(summoner_name, region)
    puuid = summoner["puuid"]
    return await get_match_ids_by_puuid(puuid, region)

@app.get("/match/{match_id}")
async def get_match(match_id: str, region: str = "na1"):
    """
    Get match by id

    Args:
        match_id (str): Match id
        region (str): Region

    Returns:
        dict: Match data
    """
    return await get_match_by_id(match_id, region)

@app.get("/match/{match_id}/timeline")
async def get_match_timeline(match_id: str, region: str = "na1"):
    """
    Get match timeline by id

    Args:
        match_id (str): Match id
        region (str): Region

    Returns:
        dict: Match timeline data
    """
    return await get_match_timeline_by_id(match_id, region)

@app.get("/summoner/{summoner_name}/matches")
async def get_matches(summoner_name: str, region: str = "na1"):
    """
    Get matches by summoner name

    Args:
        summoner_name (str): Summoner name
        region (str): Region

    Returns:
        list: Match ids
    """
    summoner = await get_summoner_info(summoner_name, region)
    puuid = summoner["puuid"]
    return await get_match_ids_by_puuid(puuid, region)

@app.get("/summoner/{summoner_name}/matches/timeline")
async def get_matches_timeline(summoner_name: str, region: str = "na1"):
    """
    Get matches timeline by summoner name

    Args:
        summoner_name (str): Summoner name
        region (str): Region

    Returns:
        list: Match ids
    """
    summoner = await get_summoner_info(summoner_name, region)
    puuid = summoner["puuid"]
    match_ids = await get_match_ids_by_puuid(puuid, region)
    match_timelines = []
    for match_id in match_ids:
        match_timelines.append(await get_match_timeline_by_id(match_id, region))
    return match_timelines

@app.get("/summoner/{summoner_name}/matches/timeline/filtered")
async def get_matches_timeline_filtered(summoner_name: str, region: str = "na1"):
    """
    Get matches timeline by summoner name

    Args:
        summoner_name (str): Summoner name
        region (str): Region

    Returns:
        list: Match ids
    """
    summoner = await get_summoner_info(summoner_name, region)
    puuid = summoner["puuid"]
    match_ids = await get_match_ids_by_puuid(puuid, region)
    match_timelines = []
    for match_id in match_ids:
        match_timelines.append(await get_match_timeline_by_id(match_id, region))
    return match_timelines