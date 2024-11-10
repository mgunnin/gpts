# TESTS CURRENTLY NOT WORKING

from unittest.mock import AsyncMock

import pytest

from app.models.summoner import Summoner
from app.scripts.data_population import process_player


@pytest.mark.asyncio
async def test_process_player():
    # Mock the necessary functions and objects
    db = AsyncMock()
    summoner_mock = AsyncMock(spec=Summoner)
    summoner_mock.summoner_name = "gameb0x"
    get_summoner_by_name_mock = AsyncMock(return_value=summoner_mock)
    populate_champion_masteries_mock = AsyncMock()
    populate_league_entries_mock = AsyncMock()
    populate_matches_mock = AsyncMock()

    # Call the process_player function
    await process_player(db=db, player=summoner_mock, region="NA")

    # Assert that the necessary functions were called with the correct arguments
    get_summoner_by_name_mock.assert_any_call("gameb0x", "NA")
    populate_champion_masteries_mock.assert_called_once_with(summoner_mock)
    populate_league_entries_mock.assert_called_once_with(summoner_mock)
    populate_matches_mock.assert_called_once(summoner_mock, "NA")
