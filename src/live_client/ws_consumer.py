"""
This file uses web sockets to communicate Live Client API data from one endpoint to the other. You can virtually put your consumer 
wherever you want, and let it process the incoming data from the producer.
"""

import argparse
import asyncio
import datetime
import json
import os
import statistics
import sys

import pandas as pd
from autogluon.tabular import TabularPredictor
from rich import print
from websockets import connect

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument(
    "-p", "--path", type=str, help="Path to predictor.pkl", required=True
)
cli_parser.add_argument(
    "-i",
    "--ip",
    type=str,
    help="IP address to make requests to",
    default="127.0.0.1",
    required=True,
)
args = cli_parser.parse_args()

# Load AutoGluon model & specify folder to store trained models.
save_path = args.path

_PREDICTOR = TabularPredictor.load(save_path)
_CURRENT_DATA = str()
_LAST_REQUESTS = list()
_LAST_PROBABILITIES = list()


async def get_info(uri):
    """
    Asynchronously connects to a WebSocket server and continuously requests and receives live client data.

    This function establishes an asynchronous connection to a WebSocket server at the specified URI. Once connected, it enters an infinite loop where it sends a request for live client data, waits for the response, and then processes the received message. The message is expected to be a JSON-formatted string representing live game data from the League of Legends client. After receiving the message, it is passed to the 'process_and_predict' function for further processing and prediction.

    Parameters:
        uri (str): The WebSocket URI to connect to. This should include the protocol (ws:// or wss://), the server's IP address or hostname, and the port number if necessary.

    Returns:
        None: This function does not return any value. It is designed to run indefinitely until manually stopped or if an error occurs that breaks the loop.

    Note:
        - This function uses the 'websockets' library for WebSocket communication. Ensure this library is installed and available in the environment.
        - The 'process_and_predict' function is called with the received message as its argument. Ensure this function is defined and can accept a string parameter.
        - The function includes error handling for connection issues. If the connection to the WebSocket server is lost, the function will attempt to reconnect.
        - The function sends a hardcoded message "get_liveclient_data" to request data from the server. Ensure the server is configured to recognize and respond to this message appropriately.
    """
    async with connect(uri) as websocket:
        while True:
            await websocket.send("get_liveclient_data")
            message = await websocket.recv()
            # print(message)
            _CURRENT_DATA = message
            process_and_predict(_CURRENT_DATA)


def main():
    asyncio.run(get_info("ws://{}:8001".format(args.ip)))


def process_and_predict(input):
    """
    Processes the input JSON string, extracts relevant game data, and predicts outcomes using a preloaded AutoGluon model.

    This function is designed to handle JSON strings representing live game data from the League of Legends client. It first decodes the JSON string into a Python dictionary. It then determines the team color of the players based on their team assignment and whether they are bots. Following this, it extracts various statistics about the active player from the JSON object, such as magic resist, health regeneration rate, spell vamp, and more. These statistics are then used to create a pandas DataFrame, which is fed into the preloaded AutoGluon model to make predictions about the outcome of the game.

    Parameters:
        input (str): A JSON string containing data from a live League of Legends match.

    Returns:
        None: This function does not return any value. Instead, it prints the expected outcome of the game (win or loss) along with the probability of that outcome.

    Note:
        - The function assumes the input JSON string is properly formatted according to the expected schema from the live client data.
        - The actual prediction logic uses the AutoGluon model preloaded in the global variable _PREDICTOR. Ensure this model is loaded before calling this function.
        - The function prints the expected outcome of the game (win or loss) along with the probability of that outcome. This is intended for logging or debugging purposes and may be adapted based on the application's requirements.
    """
    json_obj = json.loads(input)
    team_color = str()
    try:
        json_obj["allPlayers"]
    except (KeyError, TypeError):
        return
    for x in json_obj["allPlayers"]:
        if x["team"] == "ORDER" and x["isBot"] == False:
            team_color = "blue"
            break
        elif x["team"] == "CHAOS" and x["isBot"] == False:
            team_color = "red"
            break

    timestamp = int(json_obj["gameData"]["gameTime"] * 1000)
    data = [
        json_obj["activePlayer"]["championStats"]["magicResist"],
        json_obj["activePlayer"]["championStats"]["healthRegenRate"],
        json_obj["activePlayer"]["championStats"]["spellVamp"],
        timestamp,
        json_obj["activePlayer"]["championStats"]["maxHealth"],
        json_obj["activePlayer"]["championStats"]["moveSpeed"],
        json_obj["activePlayer"]["championStats"]["attackDamage"],
        json_obj["activePlayer"]["championStats"]["armorPenetrationPercent"],
        json_obj["activePlayer"]["championStats"]["lifeSteal"],
        json_obj["activePlayer"]["championStats"]["abilityPower"],
        json_obj["activePlayer"]["championStats"]["resourceValue"],
        json_obj["activePlayer"]["championStats"]["magicPenetrationFlat"],
        json_obj["activePlayer"]["championStats"]["attackSpeed"],
        json_obj["activePlayer"]["championStats"]["currentHealth"],
        json_obj["activePlayer"]["championStats"]["armor"],
        json_obj["activePlayer"]["championStats"]["magicPenetrationPercent"],
        json_obj["activePlayer"]["championStats"]["resourceMax"],
        json_obj["activePlayer"]["championStats"]["resourceRegenRate"],
    ]
    columns = [
        "magicResist",
        "healthRegenRate",
        "spellVamp",
        "timestamp",
        "maxHealth",
        "moveSpeed",
        "attackDamage",
        "armorPenetrationPercent",
        "lifesteal",
        "abilityPower",
        "resourceValue",
        "magicPenetrationFlat",
        "attackSpeed",
        "currentHealth",
        "armor",
        "magicPenetrationPercent",
        "resourceMax",
        "resourceRegenRate",
    ]
    column_names = [x.upper() for x in columns]

    sample_df = pd.DataFrame([data], columns=column_names)
    prediction = _PREDICTOR.predict(sample_df)
    pred_probs = _PREDICTOR.predict_proba(sample_df)

    expected_result = prediction.get(0)

    if len(_LAST_REQUESTS) > 100:
        _LAST_REQUESTS.pop(0)
    if len(_LAST_PROBABILITIES) > 100:
        _LAST_PROBABILITIES.pop(0)

    _LAST_REQUESTS.append(expected_result)
    _LAST_PROBABILITIES.append(
        pred_probs.iloc[0][1] * 100
    )  # winning probabilities are stored

    list_mode = int()
    try:
        list_mode = statistics.mode(_LAST_REQUESTS)
    except ValueError as e:
        print(e)
        return
    info = {
        "100_average_prediction": list_mode,
        "100_average_probability": "{:.2f}".format(
            sum(_LAST_PROBABILITIES) / len(_LAST_PROBABILITIES)
        ),
    }
    print(
        "[bold {}]TEAM {}[/bold {}] [{}]: {}".format(
            team_color, team_color.upper(), team_color, datetime.datetime.now(), info
        )
    )

    # Expected_result(1=win, 0=loss), win %, loss %
    return (
        expected_result,
        pred_probs.iloc[0][1],
        pred_probs.iloc[0][0],
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
