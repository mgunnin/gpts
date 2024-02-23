import os

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_summoner_info():
    response = client.get("/summoner/gameb0x")
    assert response.status_code == 200
    assert response.json()["name"] == "gameb0x"


def test_get_champion_mastery():
    response = client.get("/champion_mastery/k_BCLNxYlH8OxUwqcHOCmHvBnGUci9cFxm2uZNgOs8vI-HcLa4BD1bBTQnPGum13wlrijcdnLH801Q")
    assert response.status_code == 200
    assert response.json()["champion_points"] == 100000


def test_get_match_list():
    response = client.get("/match_list/1234567890")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_get_match_detail():
    response = client.get("/match_detail/1234567890123456789")
    assert response.status_code == 200
    assert response.json()["match_id"] == "1234567890123456789"


def test_calculate_performance():
    response = client.post("/performance", json={"match_id": "1234567890123456789"})
    assert response.status_code == 200
    assert response.json()["average_damage_per_minute"] == 100


if __name__ == "__main__":
    unittest.main()
