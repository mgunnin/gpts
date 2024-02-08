"""
This file uses web sockets to communicate Live Client API data from one endpoint to the other. You can virtually put your consumer 
wherever you want, and let it process the incoming data from the producer.
"""

import argparse
import asyncio
import datetime
import json
from pathlib import Path

import pandas as pd
import requests
import websockets
from rich import print

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument(
    "-i", "--ip", type=str, help="IP address to make requests to", required=True
)
args = cli_parser.parse_args()


def build_object(content):
    """
    Processes the given content to build and return a structured JSON object.

    This function is designed to take a string input, validate its type, and then attempt to fetch live game data from a predefined URL. If the fetch is successful, it processes this data by removing certain elements (e.g., 'items' from each player's data to avoid quotation marks issues) and then returns the modified content as a JSON object. If the input is not a string or the fetch fails due to a connection error, it returns an empty JSON object as a string.

    Parameters:
        content (str): The content that triggers the data fetching and processing. Its actual value is not used; it only serves to initiate the process.

    Returns:
        str: A JSON-formatted string representing the processed live game data. If the input is not a string or the fetch fails, it returns "{}".

    Raises:
        AssertionError: If the input 'content' is not of type string.
        requests.exceptions.ConnectionError: If there is a connection error when attempting to fetch the live game data.

    Note:
        The function makes a GET request to a hardcoded URL which is expected to return live game data in JSON format. This URL is specific to the League of Legends live client data API. The 'verify=False' parameter in the request disables SSL certificate verification, which may be necessary for local testing but is not recommended for production environments due to security concerns.
    """
    try:
        assert type(content) == type(str())
    except AssertionError:
        return "{}"
    try:
        response = requests.get(
            "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
        )
    except requests.exceptions.ConnectionError:
        print("{} | Currently not in game".format(datetime.datetime.now()))
        return "{}"
    # We convert to JSON format
    content = response.json()
    print("{} {}".format("x" * 5, content))
    for x in content["allPlayers"]:
        del x["items"]

    print("Content: {}".format(content))
    return content


async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)

        if message == "get_liveclient_data":
            result = build_object(message)
        else:
            result = {}

        await websocket.send(json.dumps(result))


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
