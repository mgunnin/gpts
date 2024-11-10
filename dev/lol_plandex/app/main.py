import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import create_tables
from app.routes import (
    champion_mastery_routes,
    league_routes,
    match_participant_routes,
    match_routes,
    summoner_routes,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(champion_mastery_routes.router)
app.include_router(league_routes.router)
app.include_router(match_routes.router)
app.include_router(match_participant_routes.router)
app.include_router(summoner_routes.router)


@app.on_event("startup")
async def startup_event():
    await create_tables()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
