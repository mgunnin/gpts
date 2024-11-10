"""
This file uses RabbitMQ message queues to communicate Live Client API data from one endpoint to the other. You can virtually put your consumer 
wherever you want, and let it process the incoming data from the producer.

Requires an AutoGluon pretrained model as --path, and an IP address (can be localhost) for testing both the receiver
and the producer in the same network.
"""

import argparse
import datetime
import json
import os
import re
import sys

import pandas as pd
import pika
from autogluon.tabular import TabularDataset, TabularPredictor
from pika.credentials import PlainCredentials

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument(
    "-p", "--path", type=str, help="Path to predictor.pkl", required=True
)
cli_parser.add_argument(
    "-i", "--ip", type=str, help="IP address to make requests to", required=True
)
args = cli_parser.parse_args()

# We load the AutoGluon model.
save_path = args.path  # specifies folder to store trained models
_PREDICTOR = TabularPredictor.load(save_path)


def main():
    """
    Establishes a connection to a RabbitMQ server and listens for incoming messages on the 'live_client' queue.

    This function sets up a connection to a RabbitMQ server using the pika library. It declares a queue named 'live_client'
    to ensure that the queue exists. It then proceeds to consume messages from this queue asynchronously. Upon receiving a message,
    it decodes the message body from bytes to a string, processes the JSON data contained within, and performs predictions using
    the preloaded AutoGluon model.

    The function is designed to run indefinitely, processing incoming messages and printing the results until manually stopped.

    Exceptions:
        pika.exceptions.StreamLostError: Handles the case where the stream to the RabbitMQ server is lost by attempting to re-establish the connection.

    Note:
        The RabbitMQ server is assumed to be running on 'localhost' with default parameters. The queue used is 'live_client'.
        This function does not return any value and is intended to be run as a standalone process.
    """
    try:

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost", heartbeat=600, blocked_connection_timeout=300
            )
        )
        channel = connection.channel()

        # declare queue, in case the receiver is initialized before the producer.
        channel.queue_declare(queue="live_client")

        def callback(ch, method, properties, body):
            print("{} | MQ Received packet".format(datetime.datetime.now()))
            process_and_predict(body.decode())

        # consume queue
        channel.basic_consume(
            queue="live_client", on_message_callback=callback, auto_ack=True
        )

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except pika.exceptions.StreamLostError:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost", heartbeat=600, blocked_connection_timeout=300
            )
        )


def process_and_predict(input):
    """
    Processes the input JSON string from the RabbitMQ message, extracts relevant game data, and predicts outcomes.

    This function takes a JSON string as input, which represents data from a live League of Legends match. It first decodes the JSON string into a Python dictionary. It then iterates through all players in the match, determining their team color (blue or red) based on their team assignment and prints each player's champion name alongside their team color.

    Subsequently, it extracts various statistics about the active player from the JSON object, such as magic resist, health regeneration rate, spell vamp, and more. These statistics are then used to create a pandas DataFrame. This DataFrame is intended to be used for making predictions using a preloaded AutoGluon model, although the actual prediction step is not implemented within this function.

    Parameters:
        input (str): A JSON string containing data from a live League of Legends match.

    Returns:
        None: This function does not return any value. It is expected that the prediction results would be handled or printed within the function in a complete implementation.

    Note:
        - The function assumes the input JSON string is properly formatted according to the expected schema from the live client data.
        - The actual prediction logic using the AutoGluon model or any other machine learning model is not included in this function and should be implemented separately.
        - The function prints the team color and champion name of all players in the match for demonstration purposes. In a production environment, this might be replaced with more relevant actions, such as logging or database insertion.
    """
    json_obj = json.loads(input)
    team_color = str()
    for x in json_obj["allPlayers"]:
        if x["team"] == "ORDER":
            team_color = "blue"
        else:
            team_color = "red"

        print("Team {}: {}".format(team_color, x["championName"]))

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

    sample_df = pd.DataFrame(
        [data],
        columns=[
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
        ],
    )
    prediction = _PREDICTOR.predict(sample_df)
    pred_probs = _PREDICTOR.predict_proba(sample_df)
    # print(type(prediction))
    # print(type(pred_probs))
    expected_result = prediction.get(0)
    if expected_result == 0:
        print("Expected LOSS, {}% probable".format(pred_probs.iloc[0][0] * 100))
    else:
        print("Expected WIN, {}% probable".format(pred_probs.iloc[0][1] * 100))

    print(
        "Win/loss probability: {}%/{}%".format(
            pred_probs.iloc[0][1] * 100, pred_probs.iloc[0][0] * 100
        )
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
