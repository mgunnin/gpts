import os

from cassiopeia import cassiopeia as cass
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from exceptions import MissingEnvironmentVariableError
from routes.cassio import cass_router
from routes.routes import router
from routes.watcher import watcher_router

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise MissingEnvironmentVariableError("RIOT_API_KEY")

# Set the Riot API key for Cassiopeia
cass.set_riot_api_key(RIOT_API_KEY)

ORIGINS = os.getenv("ORIGINS")
if not ORIGINS:
    raise MissingEnvironmentVariableError("ORIGINS")

origins = ORIGINS.split(",")

app = FastAPI()

app.include_router(router)
app.include_router(cass_router)
app.include_router(watcher_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
