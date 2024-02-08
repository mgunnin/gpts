import datetime
import json
import pathlib
import time

import pandas as pd
import requests
import urllib3
from autogluon.tabular import TabularDataset, TabularPredictor
from rich import print

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
urllib3.disable_warnings()


import argparse

# Specify model path here,
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument(
    "-m",
    "--model_path",
    type=str,
    help="path to the trained model",
    required=False,
    default="H:/Downloads/live1/",
)
args = parser.parse_args()


def build_object(content):
    """
    Processes the raw JSON response from the League of Legends live client API and constructs a simplified object.

    This function takes the raw JSON response from the League of Legends live client API, represented as a string, and processes it to construct a simplified Python dictionary object. The simplification process involves parsing the JSON string into a dictionary, iterating over the 'allPlayers' list to remove the 'items' field from each player's data to streamline the object, and then constructing a new dictionary that only includes the 'activePlayer', 'allPlayers', and 'gameData' fields from the original data.

    The purpose of this function is to prepare the data for further processing or analysis by reducing its complexity and focusing on the most relevant information.

    Parameters:
        content (str): The raw JSON response from the League of Legends live client API as a string.

    Returns:
        dict: A simplified dictionary object containing only the 'activePlayer', 'allPlayers', and 'gameData' fields from the original JSON response. The 'items' field is removed from each player in 'allPlayers'.

    Raises:
        ValueError: If the input is not a valid JSON string or if essential fields are missing in the parsed JSON object.

    Example:
        >>> raw_json = '{"activePlayer": {...}, "allPlayers": [...], "gameData": {...}}'
        >>> simplified_obj = build_object(raw_json)
        >>> print(simplified_obj.keys())
        dict_keys(['activePlayer', 'allPlayers', 'gameData'])
    """
    content = response.json()
    for x in content["allPlayers"]:
        del x["items"]  # Delete items to avoid quotation marks
    built_obj = {
        "activePlayer": content["activePlayer"],
        "allPlayers": content["allPlayers"],
        "gameData": content["gameData"],
    }
    content = json.dumps(content)
    content = content.replace("'", '"')
    # print('OK {}'.format(content))
    return built_obj


"""
    'duration': duration_m,
    'f1': deaths_per_min,
    'f2': k_a_per_min,
    'f3': level_per_min,
    'f4': total_damage_per_min,
    'f5': gold_per_min,
"""


def parse_object(obj):
    """
    Parses the game object to extract and calculate specific metrics.

    This function takes a game object, which is a dictionary containing details about a League of Legends match, and calculates various metrics based on the game data. These metrics include the duration of the game in minutes, deaths per minute, kills and assists per minute (K+A per min), and the level per minute for the active player. It then constructs a dictionary containing the champion name of the first player in 'allPlayers', along with the calculated metrics.

    Parameters:
        obj (dict): A dictionary representing the game object. It must contain 'gameData', 'activePlayer', and 'allPlayers' keys.

    Returns:
        dict: A dictionary containing the champion name of the first player and the calculated metrics: duration of the game in minutes ('duration'), deaths per minute ('f1'), kills and assists per minute ('f2'), and level per minute ('f3').

    Raises:
        KeyError: If the input dictionary does not contain the required keys.

    Example:
        >>> game_obj = {
        ...     "gameData": {"gameTime": 1800},
        ...     "activePlayer": {"level": 10},
        ...     "allPlayers": [{"championName": "Ahri", "scores": {"deaths": 5, "kills": 10, "assists": 5}}],
        ... }
        >>> parse_object(game_obj)
        {
            'championName': 'Ahri',
            'duration': 30.0,
            'f1': 0.16666666666666666,
            'f2': 0.5,
            'f3': 0.3333333333333333
        }
    """
    # print(obj['gameData']['gameTime'])
    duration = obj["gameData"]["gameTime"] / 60

    deaths_per_min = obj["allPlayers"][0]["scores"]["deaths"] / duration
    k_a_per_min = (
        obj["allPlayers"][0]["scores"]["kills"]
        + obj["allPlayers"][0]["scores"]["assists"]
    ) / duration
    level_per_min = obj["activePlayer"]["level"] / duration

    f1 = deaths_per_min
    f2 = k_a_per_min
    f3 = level_per_min

    relevant_data = {
        "championName": obj["allPlayers"][0]["championName"],
        "f1": f1,
        "f2": f2,
        "f3": f3,
        "duration": duration,
    }

    # print(relevant_data)

    # obj['activePlayer']['level']
    # obj['allPlayers'][0]['scores']['kills']
    # obj['allPlayers'][0]['scores']['deaths']
    # obj['allPlayers'][0]['scores']['assists']
    # obj['allPlayers'][0]['scores']['creepScore']
    return relevant_data
    # except Exception as e:
    #    print(e)


def calculate_insights(value, threshold_list: list(), description):
    """
    Calculates performance insights based on a given value and a list of thresholds.

    This function evaluates a numeric value against a predefined set of thresholds to categorize the performance into
    different levels. It returns a string describing the performance level along with a custom description.

    Parameters:
        value (float): The numeric value to evaluate.
        threshold_list (list of float): A list containing three float values that represent the thresholds for categorizing
        the performance.
        The list must be in ascending order where:
            - The first element is the threshold for 'TERRIBLE'.
            - The second element is the threshold for 'NOT SO GOOD'.
            - The third element is the threshold for 'EXCELLENT'.
            = The fourth element is the threshold for 'GOOD'.
        description (str): A custom description that is appended to the performance level string.

    Returns:
        str: A string describing the performance level. The format is '<PERFORMANCE_LEVEL> <description>', where
             <PERFORMANCE_LEVEL> can be 'TERRIBLE', 'NOT SO GOOD', 'GOOD', or 'EXCELLENT'.

    Raises:
        AssertionError: If the 'threshold_list' does not contain exactly three elements.

    Example:
        >>> calculate_insights(0.2, [0.1, 0.3, 0.5], 'in efficiency')
        'GOOD in efficiency'
    """
    assert len(threshold_list) == 3
    performance_str = str()
    if value < threshold_list[0]:
        if value < threshold_list[1]:
            performance_str = "TERRIBLE {}".format(description)
        else:
            performance_str = "NOT SO GOOD {}".format(description)
    else:
        if value > threshold_list[2]:
            performance_str = "EXCELLENT {}".format(description)
        else:
            performance_str = "GOOD {}".format(description)
    return performance_str


def predict(obj, predictor):
    assert type(obj) == type(dict())

    game_duration = obj["duration"]
    del obj["duration"]

    df = pd.DataFrame.from_dict([obj])

    df = TabularDataset(df)

    # print(df.head(1))

    result = predictor.predict(df)

    current_performance = predictor.predict(df).iloc[0]
    status = str()
    if current_performance < 49.39:
        status = "[LOSE]"
        if current_performance < 33.95:
            status += "[HARD]"
    elif current_performance >= 49.39:
        status = "[WIN]"
        if current_performance > 65.10:
            status += "[HARD]"

    """ taken from my dataset:

    calculated_player_performance	f1	f2	f3
    count	427984.000000	427984.000000	427984.000000	427984.000000
    mean	49.330796	0.200415	0.483173	0.514130
    std	22.320705	0.105837	0.244079	0.082497
    min	-111.160000	0.000000	0.000000	0.025222
    25%	33.950000	0.126134	0.306988	0.462111
    50%	49.390000	0.194691	0.466420	0.505454
    75%	65.100000	0.267318	0.639247	0.555198
    max	227.950000	1.209217	3.627652	4.508792
    """

    # Also, extract detailed insights on f1, f2, f3
    threshold_f1 = [0.194691, 0.126134, 0.267318]
    threshold_f2 = [0.466420, 0.306988, 0.639247]
    threshold_f3 = [0.505454, 0.462111, 0.555198]

    f1_performance = str()
    f2_performance = str()
    f3_performance = str()

    print(obj)

    # Since f1 and f2 can have zero-values, we need to make sure we don't misinterpret this as having a terrible performance.
    if obj["f1"] == 0.0:
        f1_performance = "NEED MORE DATA TO COMPUTE death ratio performance"
    else:
        f1_performance = calculate_insights(obj["f1"], threshold_f1, "death ratio")

    if obj["f2"] == 0.0:
        f2_performance = "NEED MORE DATA TO COMPUTE kills + assists performance"
    else:
        f2_performance = calculate_insights(obj["f2"], threshold_f2, "kills + assists")

    if game_duration < 2:
        f3_performance = "NEED MORE DATA TO COMPUTE XP performance"
    else:
        f3_performance = calculate_insights(obj["f3"], threshold_f3, "xp")

    print("[{}][DR] {}".format(datetime.datetime.now(), f1_performance))
    print("[{}][K/A] {}".format(datetime.datetime.now(), f2_performance))
    print("[{}][XP] {}".format(datetime.datetime.now(), f3_performance))

    status += " by {}%".format(abs(50 - current_performance))
    print("[{}] {}".format(datetime.datetime.now(), status))

    # So, depending on these statistics, user will receive a feedback based on q1, q2, q3


# Load saved model from disk.
predictor = TabularPredictor.load(args.model_path, require_py_version_match=False)

while True:
    try:
        response = requests.get(
            "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
        )
    except requests.exceptions.ConnectionError:
        print("{} | Currently not in game".format(datetime.datetime.now()))
        time.sleep(5)
        continue

    if response.status_code != 404:
        result = build_object(response.content)
        result = parse_object(result)
        predict(result, predictor)
    time.sleep(2)
