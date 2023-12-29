from fastapi.testclient import TestClient
from main import app, get_api_response
import os
import asyncio

client = TestClient(app)


def test_user_input():
    response = client.get("/user_input?summoner_name=gameb0x&region=na1")
    assert response.status_code == 200
    assert response.json() == {
        "summoner_name": "gameb0x",
        "region": "na1",
        "mass_region": "americas",
    }


def test_get_summoner_info():
    response = client.get("/summoner/gameb0x?region=na1")
    assert response.status_code == 200
    # The actual response from the Riot API will contain more fields
    # Here we're just checking that the response is a dictionary and contains the 'id' field
    assert isinstance(response.json(), dict)
    assert "id" in response.json()


async def test_get_api_response():
    url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/gameb0x"
    headers = {"X-Riot-Token": os.getenv("RIOT_API_KEY")}
    response = await get_api_response(url, headers)
    assert response is not None
    # The actual response from the Riot API will contain more fields
    # Here we're just checking that the response is a dictionary and contains the 'id' field
    assert isinstance(response, dict)
    assert "id" in response


# Run the async test using asyncio.run
if __name__ == "__main__":
    asyncio.run(test_get_api_response())
