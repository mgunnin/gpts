import unittest
import requests_mock
from lol_api import LolAPI

class TestLolAPI(unittest.TestCase):
    def setUp(self):
        self.api = LolAPI("test_api_key")
        self.player_name = "test_player"
        self.account_id = "test_account_id"
        self.match_id = "test_match_id"

    @requests_mock.Mocker()
    def test_get_account_id(self, m):
        url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{self.player_name}?api_key=test_api_key"
        m.get(url, json={'accountId': self.account_id})
        result = self.api.get_account_id(self.player_name)
        self.assertEqual(result, self.account_id)

    @requests_mock.Mocker()
    def test_get_match_history(self, m):
        url = f"https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{self.account_id}?api_key=test_api_key"
        m.get(url, json={'matches': [{'gameId': self.match_id}]})
        result = self.api.get_match_history(self.account_id)
        self.assertEqual(result, [self.match_id])

    @requests_mock.Mocker()
    def test_get_match_details(self, m):
        url = f"https://na1.api.riotgames.com/lol/match/v4/matches/{self.match_id}?api_key=test_api_key"
        m.get(url, json={'matchId': self.match_id})
        result = self.api.get_match_details(self.match_id)
        self.assertEqual(result, {'matchId': self.match_id})

    @requests_mock.Mocker()
    def test_get_player_stats(self, m):
        url1 = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{self.player_name}?api_key=test_api_key"
        url2 = f"https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{self.account_id}?api_key=test_api_key"
        url3 = f"https://na1.api.riotgames.com/lol/match/v4/matches/{self.match_id}?api_key=test_api_key"
        m.get(url1, json={'accountId': self.account_id})
        m.get(url2, json={'matches': [{'gameId': self.match_id}]})
        m.get(url3, json={'matchId': self.match_id})
        result = self.api.get_player_stats(self.player_name)
        self.assertEqual(result, [{'matchId': self.match_id}])


if __name__ == '__main__':
    unittest.main()
