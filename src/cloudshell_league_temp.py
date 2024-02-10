import argparse
import datetime
import os
import random
import sqlite3
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from init_db import run_init_db

conn = sqlite3.connect("lol_gpt_dev.db")

load_dotenv()

run_init_db()

riot_api_key = os.getenv("RIOT_API_KEY")


home = str(Path.home())
p = os.path.abspath("..")
sys.path.insert(1, p)
parser = argparse.ArgumentParser()
parser.add_argument(
    "-m",
    "--mode",
    help="Mode to execute",
    choices=[
        "player_list",
        "match_list",
        "match_download_standard",
        "match_download_detail",
        "process_predictor",
        "process_predictor_liveclient",
    ],
    required=False,
)
args = parser.parse_args()


request_regions = [
    "br1",
    "eun1",
    "euw1",
    "jp1",
    "kr",
    "la1",
    "la2",
    "na1",
    "oc1",
    "ru",
    "tr1",
]


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": riot_api_key,
}


def get_puuid(request_ref, summoner_name, region, db):
    request_url = (
        "https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}".format(
            request_ref, summoner_name, region
        )
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        pass
    elif response.status_code == 404:
        print(
            "{} PUUID not found for summoner {}".format(
                time.strftime("%Y-%m-%d %H:%M"), summoner_name
            )
        )
        db.delete("summoner", "summonerName", summoner_name)
    else:
        print(
            "{} Request error (@get_puuid). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )
        return
    puuid = response.json().get("puuid")
    return puuid


def get_summoner_information(summoner_name, request_region):
    assert request_region in request_regions

    request_url = (
        "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(
            request_region, summoner_name
        )
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        print(
            "{} Request error (@get_summoner_information). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )
        return None
    return response.json().get("puuid")


def get_champion_mastery(encrypted_summoner_id, request_region):
    assert request_region in request_regions

    request_url = "https://{}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{}".format(
        request_region, encrypted_summoner_id
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
    else:
        print(
            "{} Request error (@get_champion_mastery). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )

    champion_df = pd.read_csv("../data/champion_ids.csv")

    print(
        "{} Total champions played: {}".format(
            time.strftime("%Y-%m-%d %H:%M"), len(response.json())
        )
    )
    for i in response.json():
        champion_name = (
            champion_df.loc[champion_df["champion_id"] == i.get("championId")][
                "champion_name"
            ]
            .to_string()
            .split("    ")[1]
        )
        print(
            "{} Champion ID {} | Champion Name {} | Mastery level {} | Total mastery points {} | Last time played {} | Points until next mastery level {} | Chest granted {} | Tokens earned {}".format(
                time.strftime("%Y-%m-%d %H:%M"),
                i.get("championId"),
                champion_name,
                i.get("championLevel"),
                i.get("championPoints"),
                datetime.datetime.fromtimestamp(i.get("lastPlayTime") / 1000).strftime(
                    "%c"
                ),
                i.get("championPointsUntilNextLevel"),
                i.get("chestGranted"),
                i.get("tokensEarned"),
            )
        )


def get_total_champion_mastery_score(encrypted_summoner_id, request_region):
    assert request_region in request_regions
    request_url = "https://{}.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/{}".format(
        request_region, encrypted_summoner_id
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
    else:
        print(
            "{} Request error (@get_total_champion_mastery_score). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )


def get_user_leagues(encrypted_summoner_id, request_region):
    assert request_region in request_regions
    request_url = (
        "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(
            request_region, encrypted_summoner_id
        )
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
    else:
        print(
            "{} Request error (@get_user_leagues). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )

    for i in response.json():
        if i.get("leaguePoints") != 100:
            print(
                "{} Queue type: {} | Rank: {} {} {} LP | Winrate: {}% | Streak {} | >100 games {} | Inactive {}".format(
                    time.strftime("%Y-%m-%d %H:%M"),
                    i.get("queueType"),
                    i.get("tier"),
                    i.get("rank"),
                    i.get("leaguePoints"),
                    (i.get("wins") / (i.get("losses") + i.get("wins"))) * 100,
                    i.get("hotStreak"),
                    i.get("veteran"),
                    i.get("inactive"),
                )
            )
        else:
            print(
                "{} Queue type: {} | Rank: {} {} {} LP - Promo standings: {}/{} | Winrate: {}% | Streak {} | >100 games {} | Inactive {}".format(
                    time.strftime("%Y-%m-%d %H:%M"),
                    i.get("queueType"),
                    i.get("tier"),
                    i.get("rank"),
                    i.get("leaguePoints"),
                    i.get("miniSeries").get("wins"),
                    i.get("miniSeries").get("losses"),
                    (i.get("wins") / (i.get("losses") + i.get("wins"))) * 100,
                    i.get("hotStreak"),
                    i.get("veteran"),
                    i.get("inactive"),
                )
            )


def get_n_match_ids(puuid, num_matches, queue_type, region):
    available_regions = ["europe", "americas", "asia"]
    queue_types = ["ranked", "tourney", "normal", "tutorial"]
    assert region in available_regions
    assert queue_type in queue_types
    assert num_matches in range(0, 991)
    returning_object = list()
    iterator = 0
    request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}".format(
        region, puuid, queue_type, iterator, 100
    )

    for x in range(int(num_matches / 100)):
        response = requests.get(request_url, headers=headers)
        if response.status_code != 200:
            print(
                "{} Request error (@get_n_match_ids). HTTP code {}: {}".format(
                    time.strftime("%Y-%m-%d %H:%M"),
                    response.status_code,
                    response.json(),
                )
            )
        for i in response.json():
            returning_object.append({"match_id": i})
        iterator = iterator + 100
        request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}".format(
            region, puuid, queue_type, iterator, 100
        )
    print(
        "[{}][API][get_n_match_ids] MATCHES {} REGION {}".format(
            time.strftime("%Y-%m-%d %H:%M"), len(returning_object), region
        )
    )
    return returning_object


def get_match_timeline(match_id, region):
    available_regions = ["europe", "americas", "asia"]
    assert region in available_regions
    request_url = (
        "https://{}.api.riotgames.com/lol/match/v5/matches/{}/timeline".format(
            region, match_id
        )
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
    else:
        print(
            "{} Request error (@get_match_timeline). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )
        return None
    return response.json()


def get_match_info(match_id, region):
    available_regions = ["europe", "americas", "asia"]
    assert region in available_regions
    request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}".format(
        region, match_id
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
    else:
        print(
            "{} Request error (@get_match_info). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )
    return response.json()


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


def get_top_players(region, queue, db):
    assert region in request_regions
    assert queue in ["RANKED_SOLO_5x5", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]
    total_users_to_insert = list()
    request_urls = [
        "https://{}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{}".format(
            region, queue
        ),
        "https://{}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{}".format(
            region, queue
        ),
        "https://{}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{}".format(
            region, queue
        ),
    ]

    for x in request_urls:
        response = requests.get(x, headers=headers)
        if response.status_code == 200:
            try:
                print(
                    "{} Region: {} | Tier: {} | Queue: {} | Total Players: {}".format(
                        time.strftime("%Y-%m-%d %H:%M"),
                        region,
                        response.json()["tier"],
                        response.json()["queue"],
                        len(response.json()["entries"]),
                    )
                )
            except KeyError:
                pass
            for y in response.json()["entries"]:
                try:
                    y["tier"] = response.json()["tier"]
                    y["request_region"] = region
                    y["queue"] = queue
                    total_users_to_insert.append(y)
                except KeyError:
                    pass
        else:
            print(
                "{} Request error (@get_top_players). HTTP code {}: {}".format(
                    time.strftime("%Y-%m-%d %H:%M"),
                    response.status_code,
                    response.json(),
                )
            )

    for x in total_users_to_insert:


        df = pd.DataFrame(x, index=[0])

        try:
            df.to_sql("player_table", db, if_exists="append", index=False)
            print("[INS]: {}".format(x["summonerName"]))
        except ValueError:
            print("[DUP]: {}".format(x["summonerName"]))
            continue
        except sqlite3.IntegrityError:
            print("[DUP]: {}".format(x["summonerName"]))
            continue


def change_column_value_by_key(db, collection_name, column_name, column_value, key):
    connection = db.get_connection()
    collection = connection.getSodaDatabase().createCollection(collection_name)
    found_doc = collection.find().key(key).getOne()
    content = found_doc.getContent()
    content[column_name] = column_value
    collection.find().key(key).replaceOne(content)
    db.close_connection(connection)


def extract_matches(region, match_id, db, key):
    available_regions = ["europe", "americas", "asia"]
    assert region in available_regions
    request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}".format(
        region, match_id
    )

    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        print(
            "{} Request error (@extract_matches). HTTP code {}".format(
                time.strftime("%Y-%m-%d %H:%M"), response.status_code
            )
        )
        return
    o_version = response.json().get("info").get("gameVersion")
    o_participants = response.json().get("info").get("participants")
    o_teams = response.json().get("info").get("teams")

    matchups = {
        "top": list(),
        "middle": list(),
        "bottom": list(),
        "utility": list(),
        "jungle": list(),
    }
    for x in o_participants:
        try:
            matchups["{}".format(x.get("individualPosition").lower())].append(
                {
                    "champion": x.get("championName"),
                    "assists": x.get("assists"),
                    "deaths": x.get("deaths"),
                    "goldEarned": x.get("goldEarned"),
                    "kills": x.get("kills"),
                    "puuid": x.get("puuid"),
                    "summonerName": x.get("summonerName"),
                    "totalDamageDealtToChampions": x.get("totalDamageDealtToChampions"),
                    "totalMinionsKilled": x.get("totalMinionsKilled"),
                    "visionScore": x.get("visionScore"),
                    "win": x.get("win"),
                }
            )
        except KeyError:
            continue
    for x, y in matchups.items():
        if len(y) != 2:
            continue
        else:
            match_id = response.json().get("metadata").get("matchId")
            to_insert_obj = {
                "p_match_id": "{}_{}".format(match_id, x),
                "data": y,
                "gameVersion": o_version,
            }
            try:
                db.insert("matchups", to_insert_obj)
            except exceptions.IntegrityError:
                print(
                    "{} Match details {} already inserted".format(
                        time.strftime("%Y-%m-%d %H:%M"), to_insert_obj.get("p_match_id")
                    )
                )
                continue
            print(
                "{} Inserted new matchup with ID {} in region {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), "{}_{}".format(match_id, x), region
                )
            )

    change_column_value_by_key(db, "match", "processed_1v1", 1, key)

    return response.json()


def player_list(db):
    for x in request_regions:
        for y in ["RANKED_SOLO_5x5", "RANKED_FLEX_SR"]:
            get_top_players(x, y, db)


def match_list(db):
    all_match_ids = list()

    query = "SELECT * FROM player_table"
    result_set = db.execute(query)
    all_summoners = result_set.fetchall()

    query = "SELECT * FROM match_table"

    random.shuffle(all_summoners)
    for x in all_summoners:
        current_summoner = x[1]
        request_region = x[11].lower()
        print(
            "[{}][INFO] SUMMONER {} REGION {}".format(
                time.strftime("%Y-%m-%d %H:%M"), current_summoner, request_region
            )
        )
        current_summoner_puuid = get_summoner_information(
            current_summoner, request_region.lower()
        )
        if current_summoner_puuid is None:
            continue
        overall_region = determine_overall_region(request_region.lower())[0]
        z_match_ids = get_n_match_ids(
            current_summoner_puuid, 990, "ranked", overall_region
        )

        try:
            pd_all_matches = pd.DataFrame(db.execute(query).fetchall()).set_axis(
                ["match_id"], axis=1
            ) 
            df = pd.DataFrame(z_match_ids)
            diff = df[~df.isin(pd_all_matches.to_numpy().flatten())]

            if len(df) != len(diff):
                print("[{}][FIX]".format(time.strftime("%Y-%m-%d %H:%M")))
        except ValueError:
            df = pd.DataFrame(z_match_ids)
            diff = df

        if not diff.empty:
            try:
                diff.to_sql("match_table", db, if_exists="append", index=False)
                print(
                    "[{}][ADD] +{}".format(time.strftime("%Y-%m-%d %H:%M"), len(diff))
                )
            except sqlite3.IntegrityError as e:
                print(
                    "[{}][DUP]: {} {}".format(
                        time.strftime("%Y-%m-%d %H:%M"), current_summoner, e
                    )
                )
                continue
        else:
            print(
                "[{}][INFO] UP TO DATE {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), current_summoner
                )
            )


def match_download_standard(db):
    collection_match = db.get_connection().getSodaDatabase().createCollection("match")
    all_match_ids = (
        collection_match.find().filter({"processed_1v1": {"$ne": 1}}).getDocuments()
    )
    for x in all_match_ids:
        overall_region, tagline = determine_overall_region(
            x.getContent().get("match_id").split("_")[0].lower()
        )
        extract_matches(overall_region, x.getContent().get("match_id"), db, x.key)


def match_download_detail(db):
    collection_match = db.get_connection().getSodaDatabase().createCollection("match")
    all_match_ids = (
        collection_match.find().filter({"processed_5v5": {"$ne": 1}}).getDocuments()
    )
    for x in all_match_ids:
        overall_region, tagline = determine_overall_region(
            x.getContent().get("match_id").split("_")[0].lower()
        )
        match_detail = get_match_timeline(
            x.getContent().get("match_id"), overall_region
        )
        if match_detail:
            db.insert("match_detail", match_detail)
            change_column_value_by_key(db, "match", "processed_5v5", 1, x.key)


def build_final_object(json_object):

    all_frames = list()

    try:
        match_id = json_object.get("metadata").get("matchId")
    except AttributeError:
        return

    winner = int()
    frames = json_object.get("info").get("frames")
    last_frame = frames[-1]
    last_event = last_frame.get("events")[-1]
    assert last_event.get("type") == "GAME_END"
    winner = last_event.get("winningTeam")

    for x in json_object.get("info").get("frames"):

        for y in range(1, 11):
            frame = {"timestamp": x.get("timestamp")}
            frame["abilityPower"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("abilityPower")
            )
            frame["armor"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("armor")
            )
            frame["armorPen"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("armorPen")
            )
            frame["armorPenPercent"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("armorPenPercent")
            )
            frame["attackDamage"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("attackDamage")
            )
            frame["attackSpeed"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("attackSpeed")
            )
            frame["bonusArmorPenPercent"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("bonusArmorPenPercent")
            )
            frame["bonusMagicPenPercent"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("bonusMagicPenPercent")
            )
            frame["ccReduction"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("ccReduction")
            )
            frame["cooldownReduction"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("cooldownReduction")
            )
            frame["health"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("health")
            )
            frame["healthMax"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("healthMax")
            )
            frame["healthRegen"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("healthRegen")
            )
            frame["lifesteal"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("lifesteal")
            )
            frame["magicPen"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("magicPen")
            )
            frame["magicPenPercent"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("magicPenPercent")
            )
            frame["magicResist"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("magicResist")
            )
            frame["movementSpeed"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("movementSpeed")
            )
            frame["power"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("power")
            )
            frame["powerMax"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("powerMax")
            )
            frame["powerRegen"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("powerRegen")
            )
            frame["spellVamp"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("championStats")
                .get("spellVamp")
            )
            frame["magicDamageDone"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("magicDamageDone")
            )
            frame["magicDamageDoneToChampions"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("magicDamageDoneToChampions")
            )
            frame["magicDamageTaken"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("magicDamageTaken")
            )
            frame["physicalDamageDone"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("physicalDamageDone")
            )
            frame["physicalDamageDoneToChampions"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("physicalDamageDoneToChampions")
            )
            frame["physicalDamageTaken"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("physicalDamageTaken")
            )
            frame["totalDamageDone"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("totalDamageDone")
            )
            frame["totalDamageDoneToChampions"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("totalDamageDoneToChampions")
            )
            frame["totalDamageTaken"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("totalDamageTaken")
            )
            frame["trueDamageDone"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("trueDamageDone")
            )
            frame["trueDamageDoneToChampions"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("trueDamageDoneToChampions")
            )
            frame["trueDamageTaken"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("damageStats")
                .get("trueDamageTaken")
            )

            frame["goldPerSecond"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("jungleMinionsKilled")
            )
            frame["jungleMinionsKilled"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("jungleMinionsKilled")
            )
            frame["level"] = x.get("participantFrames").get("{}".format(y)).get("level")
            frame["minionsKilled"] = (
                x.get("participantFrames").get("{}".format(y)).get("minionsKilled")
            )
            frame["participantId"] = (
                x.get("participantFrames").get("{}".format(y)).get("participantId")
            )
            frame["timeEnemySpentControlled"] = (
                x.get("participantFrames")
                .get("{}".format(y))
                .get("timeEnemySpentControlled")
            )
            frame["totalGold"] = (
                x.get("participantFrames").get("{}".format(y)).get("totalGold")
            )
            frame["xp"] = x.get("participantFrames").get("{}".format(y)).get("xp")

            frame["identifier"] = "{}_{}".format(match_id, frame["participantId"])

            if winner == 100:
                if y in (1, 2, 3, 4, 5):
                    frame["winner"] = 1
                else:
                    frame["winner"] = 0
            elif winner == 200:
                if y in (1, 2, 3, 4, 5):
                    frame["winner"] = 0
                else:
                    frame["winner"] = 1
            all_frames.append(frame)
            del frame

    return all_frames


def build_final_object_liveclient(json_object):
    all_frames = list()
    match_id = str()
    match_id = json_object.get("metadata").get("matchId")

    winner = int()
    frames = json_object.get("info").get("frames")
    last_frame = frames[-1]
    last_event = last_frame.get("events")[-1]
    assert last_event.get("type") == "GAME_END"
    winner = last_event.get("winningTeam")

    for x in json_object.get("info").get("frames"):

        for y in range(1, 11):
            frame = {"timestamp": x.get("timestamp")}
            try:
                frame["abilityPower"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("abilityPower")
                )
                frame["armor"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("armor")
                )
                frame["armorPenetrationFlat"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("armorPen")
                )
                frame["armorPenetrationPercent"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("armorPenPercent")
                )
                frame["attackDamage"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("attackDamage")
                )
                frame["attackSpeed"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("attackSpeed")
                )
                frame["bonusArmorPenetrationPercent"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("bonusArmorPenPercent")
                )
                frame["bonusMagicPenetrationPercent"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("bonusMagicPenPercent")
                )
                frame["cooldownReduction"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("cooldownReduction")
                )
                frame["currentHealth"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("health")
                )
                frame["maxHealth"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("healthMax")
                )
                frame["healthRegenRate"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("healthRegen")
                )
                frame["lifesteal"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("lifesteal")
                )
                frame["magicPenetrationFlat"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("magicPen")
                )
                frame["magicPenetrationPercent"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("magicPenPercent")
                )
                frame["magicResist"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("magicResist")
                )
                frame["moveSpeed"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("movementSpeed")
                )
                frame["resourceValue"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("power")
                )
                frame["resourceMax"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("powerMax")
                )
                frame["resourceRegenRate"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("powerRegen")
                )
                frame["spellVamp"] = (
                    x.get("participantFrames")
                    .get("{}".format(y))
                    .get("championStats")
                    .get("spellVamp")
                )
                frame["identifier"] = "{}_{}".format(
                    match_id,
                    x.get("participantFrames").get("{}".format(y)).get("participantId"),
                )
            except AttributeError as e:
                print(
                    "{} [DBG] LIVECLIENT BUILDING OBJECT FAILED: {}".format(
                        time.strftime("%Y-%m-%d %H:%M"), e
                    )
                )
                return list()

            if winner == 100:
                if y in (1, 2, 3, 4, 5):
                    frame["winner"] = 1
                else:
                    frame["winner"] = 0
            elif winner == 200:
                if y in (1, 2, 3, 4, 5):
                    frame["winner"] = 0
                else:
                    frame["winner"] = 1
            all_frames.append(frame)
            del frame

    return all_frames


# CLASSIFIER MODEL (NO LIVE CLIENT API STRUCTURE)
def process_predictor(db):
    connection = db.get_connection()
    matches = connection.getSodaDatabase().createCollection("match_detail")

    for doc in matches.find().filter({"classifier_processed": {"$ne": 1}}).getCursor():
        content = doc.getContent()
        built_object = build_final_object(content)
        if built_object:
            for x in built_object:
                res = db.insert("predictor", x)
                if res == -1:
                    print(
                        "{} {}".format(
                            time.strftime("%Y-%m-%d %H:%M"),
                            doc.getContent().get("metadata").get("matchId"),
                        )
                    )
                    change_column_value_by_key(
                        db, "match_detail", "classifier_processed", 1, doc.key
                    )
                    break
    db.close_connection(connection)


def process_predictor_liveclient(db):
    connection = db.get_connection()
    matches = connection.getSodaDatabase().createCollection("match_detail")
    print(
        "{} Total match_detail documents (to process): {}".format(
            time.strftime("%Y-%m-%d %H:%M"),
            matches.find()
            .filter({"classifier_processed_liveclient": {"$ne": 1}})
            .count(),
        )
    )

    for doc in (
        matches.find()
        .filter({"classifier_processed_liveclient": {"$ne": 1}})
        .getCursor()
    ):
        content = doc.getContent()
        built_object = build_final_object_liveclient(content)
        if built_object:
            for x in built_object:
                res = db.insert("predictor_liveclient", x)
                if res == -1:
                    print(doc.getContent().get("metadata").get("matchId"))
                    change_column_value_by_key(
                        db,
                        "match_detail",
                        "classifier_processed_liveclient",
                        1,
                        doc.key,
                    )
                    break
    db.close_connection(connection)


def data_mine(db):
    if args.mode == "player_list":
        player_list(db)
    elif args.mode == "match_list":
        match_list(db)
    else:
        player_list(db)
        match_list(db)


def main():

    conn = sqlite3.connect("lol_gpt_dev.db")

    data_mine(conn)
    player_list(conn)
    match_list(conn)
    conn.close()


if __name__ == "__main__":
    main()
