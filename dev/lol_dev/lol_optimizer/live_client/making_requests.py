import datetime
import json
import time

import requests
import urllib3

urllib3.disable_warnings()


def build_object(content):
    """
    Transforms the raw JSON response from the League of Legends live client API into a simplified JSON object.

    This function takes the raw JSON response from the League of Legends live client API, processes it, and constructs a simplified JSON object. The simplification involves retaining only the 'activePlayer' and 'allPlayers' data from the original response. Additionally, it removes the 'items' field from each player in 'allPlayers' to streamline the data structure. The resulting JSON object is then converted to a string with double quotes for JSON compliance.

    Parameters:
        content (dict): The raw JSON response from the League of Legends live client API as a dictionary.

    Returns:
        str: A JSON string representing the simplified version of the original JSON response. The returned JSON string uses double quotes to ensure JSON compliance.

    Note:
        This function assumes that the input 'content' is a valid JSON object and contains the 'activePlayer' and 'allPlayers' keys. It also assumes that each player in 'allPlayers' contains an 'items' field that needs to be removed.
    """
    content = response.json()
    for x in content["allPlayers"]:
        del x["items"]  # delete items to avoid quotation marks
    built_obj = {
        "activePlayer": content["activePlayer"],
        "allPlayers": content["allPlayers"],
    }
    content = json.dumps(content)
    content = content.replace("'", '"')
    print(content)
    return content


while True:
    try:
        response = requests.get(
            "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
        )
    except requests.exceptions.ConnectionError:
        # Try again every 5 seconds
        print("{} | Currently not in game".format(datetime.datetime.now()))
        time.sleep(5)
        continue

    # Display result
    if response.status_code != 404:
        build_object(response.content)
    time.sleep(10)  # wait 10 seconds before making another request
