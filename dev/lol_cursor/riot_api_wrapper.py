import os
from typing import Any, Dict, List

import requests


class RiotAPIWrapper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://{}.api.riotgames.com/lol/"
        self.headers = {"X-Riot-Token": self.api_key}

    def _request(
        self, region: str, endpoint: str, params: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        url = self.base_url.format(region) + endpoint
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def determine_mass_region(self, region):
        mass_region = str()
        tagline = str()
        if region in ["euw1", "eun1", "ru", "tr1"]:
            mass_region = "europe"
        elif region in ["br1", "la1", "la2", "na1"]:
            mass_region = "americas"
        elif region in ["jp1", "kr"]:
            mass_region = "asia"
        elif region in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]:
            mass_region = "sea"
        else:
            mass_region = "asia"
        if region in ["br1", "jp1", "kr", "la1", "la2", "ru", "na1", "tr1", "oc1"]:
            tagline = region.upper()
        elif region == "euw1":
            tagline = "EUW"
        elif region == "eun1":
            tagline = "EUNE"
        return mass_region, tagline

    def get_summoner_by_name(self, region: str, summoner_name: str) -> Dict[str, Any]:
        """
        Retrieves summoner data from the Riot Games API based on the summoner name and region provided.

        Args:
            region (str): The region where the summoner is located.
            summoner_name (str): The name of the summoner.

        Returns:
            Dict[str, Any]: The summoner data retrieved from the Riot Games API.

        Raises:
            Exception: If the response status code is not successful.
        """
        endpoint = f"summoner/v4/summoners/by-name/{summoner_name}"
        return self._request(region, endpoint)

    def get_summoner_by_puuid(self, region: str, puuid: str) -> Dict[str, Any]:
        endpoint = f"summoner/v4/summoners/by-puuid/{puuid}"
        return self._request(region, endpoint)

    def get_account_by_puuid(self, region: str, puuid: str) -> Dict[str, Any]:
        mass_region, _ = self.determine_mass_region(region)
        endpoint = f"riot/account/v1/accounts/by-puuid/{puuid}"
        return self._request(mass_region, endpoint)

    def get_champion_mastery_by_summoner(
        self, region: str, puuid: str
    ) -> Dict[str, Any]:
        """
        Retrieves the champion mastery data for a given summoner in the game League of Legends.

        Args:
            region (str): The region where the summoner is located.
            summoner_id (str): The ID of the summoner.

        Returns:
            Dict[str, Any]: The champion mastery data for the summoner. Each dictionary contains information such as the champion ID, champion level, champion points, last play time, whether a chest has been granted, and tokens earned.
        """
        endpoint = f"champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return self._request(region, endpoint)

    def get_match_ids_by_puuid(
        self, region: str, puuid: str, start: int = 0, count: int = 20
    ) -> Dict[str, Any]:
        mass_region, _ = self.determine_mass_region(region)
        endpoint = f"match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        return self._request(mass_region, endpoint)

    def get_match_details_by_match_id(
        self, region: str, match_id: str
    ) -> Dict[str, Any]:
        mass_region, _ = self.determine_mass_region(region)
        endpoint = f"match/v5/matches/{match_id}"
        return self._request(mass_region, endpoint)

    def get_league_info_by_summoner(
        self, region: str, summoner_id: str
    ) -> Dict[str, Any]:
        endpoint = f"league/v4/entries/by-summoner/{summoner_id}"
        return self._request(region, endpoint)

    def get_matchlist_by_puuid(
        self, region: str, puuid: str, start: int = 0, count: int = 20
    ) -> List[Dict[str, Any]]:
        match_ids = self.get_match_ids_by_puuid(region, puuid, start, count)
        matchlist = []
        for match_id in match_ids:
            match_details = self.get_match_details_by_match_id(region, match_id)
            matchlist.append({"id": match_id, "details": match_details})
        return matchlist

    def get_top_players(self, region: str, queue: str, count: int) -> List[str]:
        endpoint = f"league/v4/challengerleagues/by-queue/{queue}"
        response = self._request(region, endpoint)
        return [entry["summonerName"] for entry in response["entries"][:count]]


if __name__ == "__main__":
    api_key = os.environ.get("RIOT_API_KEY", "")
    riot_api = RiotAPIWrapper(api_key)
    region = "na1"
    summoner_name = "gameb0x"
    summoner_info = riot_api.get_summoner_by_name(region, summoner_name)
    print(summoner_info)
