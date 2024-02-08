"""
This file uses RabbitMQ message queues to communicate Live Client API data from one endpoint to the other. You can virtually put your consumer 
wherever you want, and let it process the incoming data from the producer.
"""

import argparse
import ast
import datetime
import json
import os
import time
from pathlib import Path

import pandas as pd
import pika
import requests
import yaml
from pika.credentials import PlainCredentials

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument(
    "-i", "--ip", type=str, help="IP address to make requests to", required=True
)
args = cli_parser.parse_args()

_MQ_NAME = "live_client"

credentials = PlainCredentials("league", "league")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        "{}".format(args.ip),
        5672,
        "/",
        credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
)
channel = connection.channel()

channel.queue_declare(queue=_MQ_NAME)


def send_message(queue_name, message):
    """
    Sends a message to a specified RabbitMQ queue.

    This function publishes a message to a RabbitMQ queue using the channel established upon connection. It formats the message as a string before sending. After publishing the message, it logs the successful operation along with the current timestamp and the message content.

    Parameters:
        queue_name (str): The name of the queue to which the message will be published. This queue should already be declared.
        message (str): The message content to be sent. This content will be converted to a string format if not already one.

    Returns:
        None

    Note:
        This function assumes that a global 'channel' variable exists, representing an open connection to a RabbitMQ server. The channel should be initialized and configured outside this function.

    Example:
        send_message('live_client', '{"activePlayer": {...}, "allPlayers": [...]}')

    This will publish the JSON string containing information about the active player and all players to the 'live_client' queue.
    """
    channel.basic_publish(
        exchange="", routing_key=queue_name, body="{}".format(message)
    )
    print("{} | MQ {} OK".format(datetime.datetime.now(), message))


def build_object(content):
    # We convert to JSON format
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

    # Send to RabbitMQ queue.
    if response.status_code != 404:
        to_send = build_object(response.content)
        send_message("live_client", to_send)
    time.sleep(30)  # wait 30 seconds before making another request
