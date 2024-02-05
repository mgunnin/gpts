import os
import unittest

from get_data import LolInterface, get_champ_mastery

# Initialize the LolInterface with a test API key
api_key = os.environ.get("RIOT_API_KEY")
region = "na1"
lol_obj = LolInterface(api_key=api_key)

summoner_ids = [
    "7SKyjHwyyrKgwvMM4tQaP72Hjwb8hveVobJfmD1aydG-2TU",
    "a1F18i8Go1rGa_xAhXbT0Cgb3JRad0KHyPO4_YubyelxpUw",
]
summid_to_puuid = {
    "7SKyjHwyyrKgwvMM4tQaP72Hjwb8hveVobJfmD1aydG-2TU": "k_BCLNxYlH8OxUwqcHOCmHvBnGUci9cFxm2uZNgOs8vI-HcLa4BD1bBTQnPGum13wlrijcdnLH801Q",
    "a1F18i8Go1rGa_xAhXbT0Cgb3JRad0KHyPO4_YubyelxpUw": "KjfxiYmrCBNdxg0-4HzubKxnzGkjZqmgWtCyGvPGC3d330t5GyIkMRjVnmOea4hHz8zhW3vBY2QA8Q",
}


class TestGetData(unittest.TestCase):
    def test_get_champ_mastery(self):
        mastery_dict = get_champ_mastery(summid_to_puuid=summid_to_puuid, points=100000)
        assert (
            mastery_dict["7SKyjHwyyrKgwvMM4tQaP72Hjwb8hveVobJfmD1aydG-2TU"]["Vayne"][
                "points"
            ]
            == 100000
        )
        assert (
            mastery_dict["a1F18i8Go1rGa_xAhXbT0Cgb3JRad0KHyPO4_YubyelxpUw"]["Vayne"][
                "points"
            ]
            == 100000
        )

        if __name__ == "__main__":
            unittest.main()
