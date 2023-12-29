from dotenv import load_dotenv
import requests
import os

# Load Environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY environment variable is not set")
summoner_name = "gameb0x"
region = "na1"
mass_region = "AMERICAS"

class LolAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://na1.api.riotgames.com/lol/"

    def get_puuid(summoner_name, region, RIOT_API_KEY):
        RIOT_API_URL = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
        resp = requests.get(RIOT_API_URL)
        resp.raise_for_status()  # Raises stored HTTPError, if one occurred

        player_info = resp.json()
        return player_info.get('puuid')

    puuid = get_puuid(summoner_name, region, RIOT_API_KEY)

    # Retrieve match ids
    def get_match_ids(puuid, mass_region, RIOT_API_KEY):
        RIOT_API_URL = f"https://{mass_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={RIOT_API_KEY}"

        resp = requests.get(RIOT_API_URL)
        resp.raise_for_status()  # Raises stored HTTPError, if one occurred

        match_ids = resp.json()
        return match_ids

    match_ids = get_match_ids(puuid, mass_region, RIOT_API_KEY)

    def get_player_stats(self, player_name):
        # Get the player's account ID
        account_id = self.get_puuid(player_name)

        # Get the player's match history
        match_history = self.get_match_history(account_id)

        # Get detailed stats for each match
        match_stats = [self.get_match_details(match_id) for match_id in match_history]
        return match_stats


    def get_match_history(self, account_id):
        url = f"{self.base_url}match/v4/matchlists/by-account/{account_id}?api_key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        if 'matches' in data:
            return [match['gameId'] for match in data['matches']]
        else:
            print("No matches found for this account.")
        return []

    def get_match_details(self, match_id):
        url = f"{self.base_url}match/v4/matches/{match_id}?api_key={self.api_key}"
        response = requests.get(url)
        data = response.json()

        return data
