import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RiotAPIWrapper:
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")
        self.base_url = "https://{}.api.riotgames.com/lol/"
        self.headers = {"X-Riot-Token": self.api_key}

    def _request(self, region, endpoint):
        """Private method to send requests to the Riot Games API."""
        url = self.base_url.format(region) + endpoint
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_summoner_by_name(self, region, summoner_name):
        """Fetch summoner details by name."""
        endpoint = f"summoner/v4/summoners/by-name/{summoner_name}"
        return self._request(region, endpoint)

    def get_champion_mastery(self, region, puuid):
        """Fetch champion mastery details for a given summoner."""
        endpoint = f"champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return self._request(region, endpoint)

    def get_league_info(self, region, summoner_id):
        """Fetch league information for a given summoner."""
        endpoint = f"league/v4/entries/by-summoner/{summoner_id}"
        return self._request(region, endpoint)

    def get_match_ids(self, puuid, count=20):
        """Fetch recent match IDs for a given summoner."""
        match_endpoint = f"match/v5/matches/by-puuid/{puuid}/ids?count={count}"
        return self._request(
            "americas", match_endpoint
        )  # Match IDs are fetched from the Americas endpoint

    def get_match_details(self, region, match_id):
        """Fetch detailed match information."""
        match_endpoint = f"match/v5/matches/{match_id}"
        return self._request(
            "americas", match_endpoint
        )  # Match details are fetched from the Americas endpoint


# Example usage
if __name__ == "__main__":
    api_wrapper = RiotAPIWrapper()
    region = "na1"
    summoner_name = "gameb0x"
    summoner_info = api_wrapper.get_summoner_by_name(region, summoner_name)
    print(summoner_info)
