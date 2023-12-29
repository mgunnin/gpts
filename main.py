import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY environment variable is not set")

app = FastAPI()
app.include_router(router)

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

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY environment variable is not set")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
