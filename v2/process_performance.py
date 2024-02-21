import multiprocessing.pool as mpool
import os
import random
import sqlite3
import sys
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from rich import print

# if reading from a csv file, we RANDOMLY SHUFFLE the dataset
# df = df.sample(frac=1)

pool = mpool.ThreadPool(19)

# Create a connection to the SQLite database
conn = sqlite3.connect("lol_gpt_v3.db", timeout=5)

query = "SELECT * FROM match_table"
result_set = conn.execute(query)
all_matches = result_set.fetchall()  # create some randomness for consequent executions
random.shuffle(all_matches)

df = pd.DataFrame(all_matches, columns=["match_id"])

conn.close()

currently_limited = 0


# Visualize dataframe
print(df.tail(3))
print("Dataframe length: {}".format(len(df)))

load_dotenv()

riot_api_key = os.getenv("RIOT_API_KEY")
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": riot_api_key,
}


# auxiliary function
def determine_overall_region(region):
    overall_region = str()
    tagline = str()
    if region in ["euw1", "eun1", "ru", "tr1"]:
        overall_region = "europe"
    elif region in ["br1", "la1", "la2", "na1"]:
        overall_region = "americas"
    else:
        overall_region = "asia"
    if region in ["br1", "jp1", "kr", "la1", "la2", "ru", "na1", "tr1", "oc1"]:
        tagline = region.upper()
    elif region == "euw1":
        tagline = "EUW"
    elif region == "eun1":
        tagline = "EUNE"
    return overall_region, tagline


def get_match_info(match_id, region):
    """
    Fetches detailed match information for a given match ID and region from the Riot Games API.

    This function constructs a request URL using the specified match ID and region, then sends a GET request to the Riot Games API to retrieve detailed match information. The function ensures that the region provided is one of the available regions (Europe, Americas, Asia) and asserts this at the beginning. It then prints the match ID for logging purposes and handles the response from the API.

    If the response status code is 200 (OK), the function proceeds without printing the response, indicating a successful API call. If the response status code is 429, it indicates that the rate limit has been exceeded, and the function sets a flag to indicate this. For any other status code, the function prints an error message with the HTTP status code to help diagnose issues.

    The function returns a tuple containing a rate limit flag and the JSON response from the API if the request was successful. If the request was not successful (e.g., due to an error status code), the function returns None to indicate failure.

    Parameters:
    - match_id (str): The unique identifier of the match for which information is being retrieved.
    - region (str): The region in which the match took place. This is used to construct the request URL.

    Returns:
    - tuple: A tuple containing a rate limit flag (0 or 1) and the JSON response from the API if the request was successful. Returns None if the request failed.

    Raises:
    - AssertionError: If the specified region is not one of the available regions (Europe, Americas, Asia).
    """
    available_regions = ["americas", "asia", "europe"]
    assert region in available_regions
    request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}".format(
        region, match_id
    )
    print(match_id)

    response = requests.get(request_url, headers=headers)

    # print(json.dumps(response.json()))
    # with open('example.txt', 'w') as f:
    #    json.dump(response.json(), f)
    rate_limited = 0
    if response.status_code == 200:
        # print('{} {}'.format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
        pass
    elif response.status_code == 429:  # rate limited
        rate_limited = 1
    else:
        print(
            "{} Request error (@get_match_info). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )
        return None
    # Return match list & write json to .txt file
    # with open('example.txt', 'w') as f:
    #    json.dump(response.json(), f)
    return rate_limited, response.json()


def process_player_performance(obj, conn):
    # Check if obj is empty. this will happen when we try to parse
    # the json object but it fails with KeyError:
    match_identifier = str()
    try:
        match_identifier = obj["info"]["gameId"]
    except KeyError:
        return
    # Check if match_identifier exists in the database
    c = conn.cursor()
    c.execute(
        "SELECT EXISTS(SELECT 1 FROM performance_table WHERE match_identifier = ?)",
        (match_identifier,),
    )
    result = c.fetchone()[0]
    if result:
        print("[DUPLICATE FOUND] {}".format(match_identifier))
        return 0
    # obj['info']['gameDuration'] # milliseconds
    # obj['participants'][0] -> everything
    # Create new dataset

    # flatten json object to csv format

    # obj['participants'][0]['win'] -> to predict and also, to predict player performance -> or take as input for now.

    for i in range(len(obj["info"]["participants"])):

        # duration_s = obj['info']['gameDuration'] / 1000 # since patch 13.1, this information is retrieved in seconds.
        duration_m = obj["info"]["gameDuration"] / 60

        deaths_per_min = obj["info"]["participants"][i]["deaths"] / duration_m
        k_a_per_min = (
            obj["info"]["participants"][i]["kills"]
            + obj["info"]["participants"][i]["assists"]
        ) / duration_m
        level_per_min = obj["info"]["participants"][i]["champLevel"] / duration_m
        total_damage_per_min = (
            obj["info"]["participants"][i]["totalDamageDealt"] / duration_m
        )
        gold_per_min = obj["info"]["participants"][i]["goldEarned"] / duration_m

        # 0.336 — (1.437 x Deaths per min) + (0.000117 x gold per min) + (0.443 x K_A per min) + (0.264 x Level per min) + (0.000013 x TD per min)
        calculated_player_performance = (
            0.336
            - (1.437 * deaths_per_min)
            + (0.000117 * gold_per_min)
            + (0.443 * k_a_per_min)
            + (0.264 * level_per_min)
            + (0.000013 * total_damage_per_min)
        )
        new_object = {
            "match_identifier": match_identifier,
            "duration": duration_m,
            "f1": deaths_per_min,
            "f2": k_a_per_min,
            "f3": level_per_min,
            "f4": total_damage_per_min,
            "f5": gold_per_min,
            "calculated_player_performance": round(
                (calculated_player_performance * 100), 2
            ),
        }
        if level_per_min > 50:
            # print(new_object)
            continue

        second_obj = obj["info"]["participants"][i]

        try:
            del second_obj["allInPings"]
        except KeyError as e:
            # print('Old Match Found: {} not found'.format(e))
            pass
        try:
            del second_obj["challenges"]
        except KeyError as e:
            pass
        try:
            del second_obj["eligibleForProgression"]
        except KeyError as e:
            pass
        try:
            del second_obj["totalAllyJungleMinionsKilled"]
        except KeyError as e:
            pass
        try:
            del second_obj["totalEnemyJungleMinionsKilled"]
        except KeyError as e:
            pass
        try:
            del second_obj["basicPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["assistMePings"]
        except KeyError as e:
            pass
        try:
            del second_obj["baitPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["commandPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["dangerPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["enemyMissingPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["enemyVisionPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["getBackPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["holdPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["needVisionPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["onMyWayPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["pushPings"]
        except KeyError as e:
            pass
        try:
            del second_obj["visionClearedPings"]
        except KeyError as e:
            pass

        final_object = second_obj | new_object
        final_object.pop(
            "perks"
        )  # remove this list as we won't use it and gives json to db decoding problems
        # print('{}: {}'.format(round((calculated_player_performance * 100), 2), json.dumps(final_object)))
        print(
            "[{}] PERF {}%".format(
                final_object["championName"],
                round((calculated_player_performance * 100), 2),
            )
        )
        sys.stdout.flush()

        # print(', '.join([f'{key} REAL' for key in final_object.keys()])) # get header for sql

        # print(final_object)
        # Use pandas to convert the final_object to a DataFrame and then to a tabular structure
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(final_object, index=[0])
        # print(df)
        # Use pandas to convert the final_object to a DataFrame and then to a tabular structure

        # print(df.columns)

        # Insert DF into SQLite table
        try:
            df.to_sql("performance_table", conn, if_exists="append", index=False)
        except ValueError:
            print("[DUPLICATE FOUND] {}".format(final_object["match_identifier"]))
            sys.stdout.flush()
            continue

    return 1


def run_process_player_performance(row):
    conn = sqlite3.connect("lol_gpt_v3.db", timeout=5)
    match_id = row
    region = determine_overall_region(str(match_id).split("_")[0].lower())[0]
    match_info = get_match_info(match_id, region)
    if match_info is None:
        rate_limited = None
        results = None
    else:
        rate_limited, results = match_info

    global currently_limited
    if rate_limited == 1:
        currently_limited = rate_limited

    if results is None:
        process_player_performance(results, conn)
        return


for i in range(1, len(df), 19):  # step 3 since our batch size = 3.
    try:
        sync_1 = df.iloc[i]
        sync_2 = df.iloc[i + 1]
        sync_3 = df.iloc[i + 2]
        sync_4 = df.iloc[i + 3]
        sync_5 = df.iloc[i + 4]
        sync_6 = df.iloc[i + 5]
        sync_7 = df.iloc[i + 6]
        sync_8 = df.iloc[i + 7]
        sync_9 = df.iloc[i + 8]
        sync_10 = df.iloc[i + 9]
        sync_11 = df.iloc[i + 10]
        sync_12 = df.iloc[i + 11]
        sync_13 = df.iloc[i + 12]
        sync_14 = df.iloc[i + 13]
        sync_15 = df.iloc[i + 14]
        sync_16 = df.iloc[i + 15]
        sync_17 = df.iloc[i + 16]
        sync_18 = df.iloc[i + 17]
        sync_19 = df.iloc[i + 18]

        # print(sync_1, sync_2, sync_3, sync_4, sync_5)
    except Exception as e:
        print(e)
    # for row, index in df.iterrows(): get the total number of active workers in the pool
    if currently_limited == 1:
        print("Rate limited. Sleeping for 2 minutes...")
        time.sleep(120)
        currently_limited = 0

    for j in range(1, 18):
        try:
            sync_var = df.iloc[i + j - 1]
            pool.apply_async(func=run_process_player_performance, args=(sync_var,))
        except IndexError as e:
            print(f"Index error at position {i + j - 1}: {e}")
    try:
        pool.apply_async(
            func=run_process_player_performance, args=(df.iloc[i + 18],)
        )  # .get() # we make sure we at least wait for one synchronous thread
    except sqlite3.OperationalError:
        print("[LOCK]")
        continue
    # Finish execution before running the next batch, otherwise 3.2 million threads would be created (size(len(df))
    # time.sleep(24) avoid being rate limited with development api key

    """
    match_id = row
    #print(match_id)
    #print(determine_overall_region(str(match_id)[0:3].lower())[0])

    (rate_limited, results) = get_match_info(match_id, determine_overall_region(str(match_id).split('_')[0].lower())[0])

    if results is None:
        iter += 1
        continue

    penalty = process_player_performance(results, conn, iter)
    print(penalty)
    if penalty:
        time.sleep(.5) # avoid being rate limited from riot

    iter += 1
    """
    # print('{}%'.format((iter / len(df))*100))
    time.sleep(21)


# pool.join()
conn.close()
