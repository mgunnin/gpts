import os

from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "RIOT_API_KEY": os.getenv("RIOT_API_KEY"),
    "DB_PATH": "lol_summoner.db",
}
