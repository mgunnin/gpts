import datetime
import os
import random
import time

import pandas as pd
import psycopg2
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from rich import print
from sqlalchemy import create_engine

load_dotenv()  # Load environment variables from .env file

# Environment variable checks
riot_api_key = os.getenv("RIOT_API_KEY")
if not riot_api_key:
    raise ValueError("RIOT_API_KEY environment variable is not set")

ORIGINS = os.getenv("ORIGINS")
if not ORIGINS:
    raise ValueError("ORIGINS environment variable is not set")

origins = ORIGINS.split(",")

# FastAPI app setup
app = FastAPI()

db = psycopg2.connect(
    host=os.environ.get("SUPABASE_URL"),
    port=os.environ.get("SUPABASE_PORT"),
    database=os.environ.get("SUPABASE_DB"),
    user=os.environ.get("SUPABASE_USER"),
    password=os.environ.get("SUPABASE_PW"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database class
class Database:
    def __init__(self):
        self.engine = self.get_sqlalchemy_engine()

    def execute_raw(self, sql, params=None):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()

    def execute(self, query, params=None):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            return cursor

    def get_connection(self):
        return psycopg2.connect(
            host=os.environ.get("SUPABASE_URL"),
            port=os.environ.get("SUPABASE_PORT"),
            database=os.environ.get("SUPABASE_DB"),
            user=os.environ.get("SUPABASE_USER"),
            password=os.environ.get("SUPABASE_PW"),
        )

    def get_sqlalchemy_engine(self):
        database_url = (
            f"postgresql+psycopg2://{os.environ.get('SUPABASE_USER')}:"
            f"{os.environ.get('SUPABASE_PW')}@{os.environ.get('SUPABASE_URL')}:"
            f"{os.environ.get('SUPABASE_PORT')}/{os.environ.get('SUPABASE_DB')}"
        )
        engine = create_engine(database_url)
        return engine

    def run_init_db(self):
        conn = self.get_connection()

        # Table definitions
        player_table_def = """
            CREATE TABLE IF NOT EXISTS player_table (
                summonerId TEXT PRIMARY KEY,
                summonerName TEXT,
                leaguePoints INTEGER,
                rank TEXT,
                wins INTEGER,
                losses INTEGER,
                veteran BOOLEAN,
                inactive BOOLEAN,
                freshBlood BOOLEAN,
                hotStreak BOOLEAN,
                tier TEXT,
                request_region TEXT,
                queue TEXT
            )
        """

        match_table_def = """
            CREATE TABLE IF NOT EXISTS match_table (
                match_id TEXT PRIMARY KEY
            )
        """

        performance_table_def = """
            CREATE TABLE IF NOT EXISTS performance_table (
                assists INTEGER,
                baronKills INTEGER,
                bountyLevel INTEGER,
                champExperience INTEGER,
                champLevel INTEGER,
                championId INTEGER,
                championName TEXT,
                championTransform INTEGER,
                consumablesPurchased INTEGER,
                damageDealtToBuildings INTEGER,
                damageDealtToObjectives INTEGER,
                damageDealtToTurrets INTEGER,
                damageSelfMitigated INTEGER,
                deaths INTEGER,
                detectorWardsPlaced INTEGER,
                doubleKills INTEGER,
                dragonKills INTEGER,
                firstBloodAssist BOOLEAN,
                firstBloodKill BOOLEAN,
                firstTowerAssist BOOLEAN,
                firstTowerKill BOOLEAN,
                gameEndedInEarlySurrender BOOLEAN,
                gameEndedInSurrender BOOLEAN,
                goldEarned INTEGER,
                goldSpent INTEGER,
                individualPosition TEXT,
                inhibitorKills INTEGER,
                inhibitorTakedowns INTEGER,
                inhibitorsLost INTEGER,
                item0 INTEGER,
                item1 INTEGER,
                item2 INTEGER,
                item3 INTEGER,
                item4 INTEGER,
                item5 INTEGER,
                item6 INTEGER,
                itemsPurchased INTEGER,
                killingSprees INTEGER,
                kills INTEGER,
                lane TEXT,
                largestCriticalStrike INTEGER,
                largestKillingSpree INTEGER,
                largestMultiKill INTEGER,
                longestTimeSpentLiving INTEGER,
                magicDamageDealt INTEGER,
                magicDamageDealtToChampions INTEGER,
                magicDamageTaken INTEGER,
                neutralMinionsKilled INTEGER,
                nexusKills INTEGER,
                nexusLost INTEGER,
                nexusTakedowns INTEGER,
                objectivesStolen INTEGER,
                objectivesStolenAssists INTEGER,
                participantId INTEGER,
                pentaKills INTEGER,
                physicalDamageDealt INTEGER,
                physicalDamageDealtToChampions INTEGER,
                physicalDamageTaken INTEGER,
                profileIcon INTEGER,
                puuid TEXT,
                quadraKills INTEGER,
                riotIdName TEXT,
                riotIdTagline TEXT,
                role TEXT,
                sightWardsBoughtInGame INTEGER,
                spell1Casts INTEGER,
                spell2Casts INTEGER,
                spell3Casts INTEGER,
                spell4Casts INTEGER,
                summoner1Casts INTEGER,
                summoner1Id INTEGER,
                summoner2Casts INTEGER,
                summoner2Id INTEGER,
                summonerId TEXT,
                summonerLevel INTEGER,
                summonerName TEXT,
                teamEarlySurrendered BOOLEAN,
                teamId INTEGER,
                teamPosition TEXT,
                timeCCingOthers INTEGER,
                timePlayed INTEGER,
                totalDamageDealt INTEGER,
                totalDamageDealtToChampions INTEGER,
                totalDamageShieldedOnTeammates INTEGER,
                totalDamageTaken INTEGER,
                totalHeal INTEGER,
                totalHealsOnTeammates INTEGER,
                totalMinionsKilled INTEGER,
                totalTimeCCDealt INTEGER,
                totalTimeSpentDead INTEGER,
                totalUnitsHealed INTEGER,
                tripleKills INTEGER,
                trueDamageDealt INTEGER,
                trueDamageDealtToChampions INTEGER,
                trueDamageTaken INTEGER,
                turretKills INTEGER,
                turretTakedowns INTEGER,
                turretsLost INTEGER,
                unrealKills INTEGER,
                visionScore INTEGER,
                visionWardsBoughtInGame INTEGER,
                wardsKilled INTEGER,
                wardsPlaced INTEGER,
                win BOOLEAN,
                match_identifier TEXT,
                duration NUMERIC,
                f1 NUMERIC,
                f2 NUMERIC,
                f3 NUMERIC,
                f4 NUMERIC,
                f5 NUMERIC,
                calculated_player_performance NUMERIC
            )
        """

        match_detail_def = """
            CREATE TABLE IF NOT EXISTS match_detail (
                match_id TEXT PRIMARY KEY,
                game_duration INTEGER,
                winning_team INTEGER,
                participants TEXT,
                participantId INTEGER,
                teamId INTEGER,
                championId INTEGER,
                championName TEXT,
                championTransform INTEGER,
                individualPosition TEXT,
                lane TEXT,
                role TEXT,
                kills INTEGER,
                deaths INTEGER,
                assists INTEGER,
                totalDamageDealt INTEGER,
                totalDamageDealtToChampions INTEGER,
                totalDamageTaken INTEGER,
                totalHeal INTEGER,
                totalMinionsKilled INTEGER,
                goldEarned INTEGER,
                goldSpent INTEGER,
                turretKills INTEGER,
                turretTakedowns INTEGER,
                turretsLost INTEGER,
                inhibitorKills INTEGER,
                inhibitorTakedowns INTEGER,
                inhibitorsLost INTEGER,
                totalTimeSpentDead INTEGER,
                visionScore INTEGER,
                wardsPlaced INTEGER,
                wardsKilled INTEGER,
                firstBloodKill BOOLEAN,
                firstBloodAssist BOOLEAN,
                firstTowerKill BOOLEAN,
                firstTowerAssist BOOLEAN,
                win BOOLEAN
            )
        """

        # Execute table creation queries
        self.execute(player_table_def)
        self.execute(match_table_def)
        self.execute(performance_table_def)
        self.execute(match_detail_def)

        conn.commit()
        conn.close()

    def change_column_value_by_key(self, table_name, column_name, column_value, key):
        connection = self.get_connection()
        cursor = connection.cursor()
        update_statement = f"UPDATE {table_name} SET {column_name} = %s WHERE key_column = %s"
        cursor.execute(update_statement, (column_value, key))
        connection.commit()
        print(
            "{} [DBG] UPDATE BIT {}: {}".format(
                time.strftime("%Y-%m-%d %H:%M"), column_name, column_value
            )
        )
        connection.close()

    def process_predictor(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM match_detail WHERE classifier_processed != 1"
        cursor.execute(query)
        matches = cursor.fetchall()
        print(
            "{} Total match_detail documents (to process): {}".format(
                time.strftime("%Y-%m-%d %H:%M"), len(matches)
            )
        )

        for doc in matches:
            content = doc[0]
            built_object = build_final_object(content)
            if built_object:
                for x in built_object:
                    try:
                        insert_query = "INSERT INTO predictor VALUES (%s)"
                        cursor.execute(insert_query, (x,))
                        print(
                            "{} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"),
                                doc[0].get("metadata").get("matchId"),
                            )
                        )
                        update_query = (
                            "UPDATE match_detail SET classifier_processed = 1 WHERE key = %s"
                        )
                        cursor.execute(update_query, (doc[0],))
                    except psycopg2.IntegrityError as e:
                        print(
                            "[{}][DUP]: {} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"), doc[0], e
                            )
                        )
                        continue
        connection.commit()
        connection.close()

    def process_predictor_liveclient(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM match_detail WHERE classifier_processed_liveclient != 1"
        cursor.execute(query)
        matches = cursor.fetchall()
        print(
            "{} Total match_detail documents (to process): {}".format(
                time.strftime("%Y-%m-%d %H:%M"), len(matches)
            )
        )

        for doc in matches:
            content = doc[0]
            built_object = build_final_object_liveclient(content)
            if built_object:
                for x in built_object:
                    try:
                        insert_query = "INSERT INTO predictor_liveclient VALUES (%s)"
                        cursor.execute(insert_query, (x,))
                        print(doc[0].get("metadata").get("matchId"))
                        update_query = (
                            "UPDATE match_detail SET classifier_processed_liveclient = 1 WHERE key = %s"
                        )
                        cursor.execute(update_query, (doc[0],))
                    except psycopg2.IntegrityError as e:
                        print(
                            "[{}][DUP]: {} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"), doc[0], e
                            )
                        )
                        continue
        connection.commit()
        connection.close()


# Riot API class
class RiotAPI:
    def __init__(self, db):
        self.db = db
        self.riot_api_key = os.getenv("RIOT_API_KEY")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": riot_api_key,
        }
        self.request_regions = [
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

    def get_puuid(self, request_ref, summoner_name, region, db):
        request_url = (
            "https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}".format(
                request_ref, summoner_name, region
            )
        )

        response = requests.get(request_url, headers=self.headers)
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

    def get_summoner_information(self, summoner_name, request_region):
        assert request_region in self.request_regions

        request_url = (
            "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(
                request_region, summoner_name
            )
        )

        response = requests.get(request_url, headers=self.headers)
        if response.status_code != 200:
            print(
                "{} Request error (@get_summoner_information). HTTP code {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), response.status_code
                )
            )
            return None
        return response.json().get("puuid")

    def get_champion_mastery(self, puuid, request_region):
        assert request_region in self.request_regions

        request_url = "https://{}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{}".format(
            request_region, puuid
        )

        response = requests.get(request_url, headers=self.headers)
        print("Request URL: {}".format(request_url))
        print("Response Status Code: {}".format(response.status_code))
        if response.status_code == 200:
            print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
        else:
            print(
                "{} Request error (@get_champion_mastery). HTTP code {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), response.status_code
                )
            )

        champion_df = pd.read_csv("data/champion_ids.csv")

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
                    datetime.datetime.fromtimestamp(i("lastPlayTime") / 1000).strftime(
                        "%c"
                    ),
                    i.get("championPointsUntilNextLevel"),
                    i.get("chestGranted"),
                    i.get("tokensEarned"),
                )
            )

    def get_total_champion_mastery_score(self, puuid, request_region):
        assert request_region in self.request_regions
        request_url = "https://{}.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{}".format(
            request_region, puuid
        )

        response = requests.get(request_url, headers=self.headers)
        if response.status_code == 200:
            print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
        else:
            print(
                "{} Request error (@get_total_champion_mastery_score). HTTP code {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), response.status_code
                )
            )

    def get_user_leagues(self, puuid, request_region):
        assert request_region in self.request_regions
        request_url = (
            "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(
                request_region, puuid
            )
        )

        response = requests.get(request_url, headers=self.headers)
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

    def get_match_ids(self, puuid, num_matches, queue_type, region):
        available_regions = ["europe", "americas", "asia"]
        queue_types = ["ranked"]
        assert region in available_regions
        assert queue_type in queue_types
        assert num_matches in range(0, 991)
        returning_object = list()
        iterator = 0
        request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start={}&count={}".format(
            region, puuid, queue_type, iterator, 100
        )

        for x in range(int(num_matches / 100)):
            response = requests.get(request_url, headers=self.headers)
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

    def get_match_timeline(self, match_id, region):
        available_regions = ["europe", "americas", "asia"]
        assert region in available_regions
        request_url = (
            "https://{}.api.riotgames.com/lol/match/v5/matches/{}/timeline".format(
                region, match_id
            )
        )

        response = requests.get(request_url, headers=self.headers)
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

    def get_match_info(self, match_id, region):
        available_regions = ["europe", "americas", "asia"]
        assert region in available_regions
        request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}".format(
            region, match_id
        )
        print(match_id)

        response = requests.get(request_url, headers=self.headers)

        rate_limited = 0
        if response.status_code == 200:
            pass
        elif response.status_code == 429:
            rate_limited = 1
        else:
            print(
                "{} Request error (@get_match_info). HTTP code {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), response.status_code
                )
            )
            return None
        return rate_limited, response.json()

    def determine_overall_region(self, region):
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

    def get_top_players(self, region, queue, db):
        assert region in self.request_regions
        assert queue in ["RANKED_SOLO_5x5"]
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
            response = requests.get(x, headers=self.headers)
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

        print(
            "{} Total users obtained in region {} and queue {}: {}".format(
                time.strftime("%Y-%m-%d %H:%M"), region, queue, len(total_users_to_insert)
            )
        )

        insert_query = """
    INSERT INTO player_table (summonerId, summonerName, leaguePoints, rank, wins, losses, veteran, inactive, freshBlood, hotStreak, tier, request_region, queue)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (summonerId) DO NOTHING
    """
        for player in total_users_to_insert:
            try:
                db.execute_raw(
                    insert_query,
                    (
                        player["summonerId"],
                        player["summonerName"],
                        player["leaguePoints"],
                        player["rank"],
                        player["wins"],
                        player["losses"],
                        player["veteran"],
                        player["inactive"],
                        player["freshBlood"],
                        player["hotStreak"],
                        player["tier"],
                        player["request_region"],
                        player["queue"],
                    ),
                )
                print("[INS]: {}".format(player["summonerName"]))
            except psycopg2.IntegrityError:
                continue

    def extract_matches(self, region, match_id, db, key):
        assert region in self.request_regions
        request_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}".format(
            region, match_id
        )

        response = requests.get(request_url, headers=self.headers)
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
                        "totalDamageDealtToChampions": x.get(
                            "totalDamageDealtToChampions"
                        ),
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
                    db.execute("INSERT INTO matchups VALUES (?)", (to_insert_obj,))
                except psycopg2.IntegrityError:
                    print(
                        "{} Match details {} already inserted".format(
                            time.strftime("%Y-%m-%d %H:%M"),
                            to_insert_obj.get("p_match_id"),
                        )
                    )
                    continue
                print(
                    "{} Inserted new matchup with ID {} in region {}".format(
                        time.strftime("%Y-%m-%d %H:%M"),
                        "{}_{}".format(match_id, x),
                        region,
                    )
                )

        db.execute("UPDATE match SET processed_1v1 = 1 WHERE key = ?", (key,))

        return response.json()

    def player_list(self):
        for x in self.request_regions:
            for y in ["RANKED_SOLO_5x5"]:
                self.get_top_players(x, y, self.db)

    def match_list(self):
        query = "SELECT * FROM player_table"
        result_set = self.db.execute(query)
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
            current_summoner_puuid = self.get_summoner_information(
                current_summoner, request_region.lower()
            )
            if current_summoner_puuid is None:
                continue
            overall_region = self.determine_overall_region(request_region.lower())[0]
            z_match_ids = self.get_match_ids(
                current_summoner_puuid, 990, "ranked", overall_region
            )

            try:
                pd_all_matches = pd.DataFrame(self.db.execute(query).fetchall()).set_axis(
                    ["match_id"], axis=1
                )
                df = pd.DataFrame(z_match_ids)
                diff = df[
                    ~df.apply(tuple, axis=1).isin(pd_all_matches.apply(tuple, axis=1))
                ]

                if len(df) != len(diff):
                    print("[{}][FIX]".format(time.strftime("%Y-%m-%d %H:%M")))
            except ValueError:
                df = pd.DataFrame(z_match_ids)
                diff = df

            if not diff.empty:
                try:
                    diff.to_sql(
                        "match_table",
                        self.db.get_connection(),
                        if_exists="append",
                        index=False,
                    )
                    print(
                        "[{}][ADD] +{}".format(
                            time.strftime("%Y-%m-%d %H:%M"), len(diff)
                        )
                    )
                except psycopg2.IntegrityError as e:
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

    def match_download_standard(self, db):
        conn = db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM match_table WHERE processed_1v1 != 1"
        all_match_ids = cursor.execute(query).fetchall()
        for x in all_match_ids:
            overall_region, tagline = self.determine_overall_region(
                x[0].split("_")[0].lower()
            )
            print(
                "{} Overall Region {} detected".format(
                    time.strftime("%Y-%m-%d %H:%M"), overall_region
                )
            )
            self.extract_matches(overall_region, x[0], db, x[0])

    def match_download_detail(self, db):
        """
        Downloads detailed match information for matches that have not been processed for 5v5 analysis.

        This function queries the 'match' table in the database for match IDs that have not been processed for 5v5
        match detail analysis (indicated by the 'processed_5v5' column not being set to 1). For each unprocessed match,
        it determines the overall region, fetches detailed match information, and inserts it into the 'match_detail'
        table. It also updates the 'processed_5v5' status for the match in the 'match' table to prevent reprocessing.

        The function handles exceptions that may occur during the database operations, such as IntegrityError, which indicates a duplicate entry attempt. In such cases, it logs the error and continues with the next match ID.

        Parameters:
            db (Database): The database object that provides a connection to the database and methods to execute database operations.

        Returns:
            None
        """
        query = "SELECT * FROM match WHERE processed_5v5 != 1"
        all_match_ids = db.execute(query).fetchall()
        for x in all_match_ids:
            overall_region, tagline = self.determine_overall_region(
                x[0].split("_")[0].lower()
            )
            print(
                "{} Overall Region {} detected".format(
                    time.strftime("%Y-%m-%d %H:%M"), overall_region
                )
            )
            match_detail = self.get_match_timeline(x[0], overall_region)
            if match_detail:
                try:
                    db.execute("INSERT INTO match_detail VALUES (?)", (match_detail,))
                    db.execute(
                        "UPDATE match SET processed_5v5 = 1 WHERE key = ?", (x[0],)
                    )
                except psycopg2.IntegrityError as e:
                    print(
                        "[{}][DUP]: {} {}".format(
                            time.strftime("%Y-%m-%d %H:%M"), x[0], e
                        )
                    )
                    continue


# Performance processing class
class ProcessPerformance:
    def __init__(self, db):
        self.db = db

    def calculate_player_performance(self, participant_data, duration_m):
        deaths_per_min = participant_data["deaths"] / duration_m
        k_a_per_min = (
            participant_data["kills"] + participant_data["assists"]
        ) / duration_m
        level_per_min = participant_data["champLevel"] / duration_m
        total_damage_per_min = participant_data["totalDamageDealt"] / duration_m
        gold_per_min = participant_data["goldEarned"] / duration_m

        calculated_player_performance = (
            0.336 - (1.437 * deaths_per_min) + (0.000117 * gold_per_min) + (0.443 * k_a_per_min) + (0.264 * level_per_min) + (0.000013 * total_damage_per_min)
        )
        return round((calculated_player_performance * 100), 2)

    def insert_performance_data(self, final_object):
        df = pd.DataFrame(final_object, index=[0])
        try:
            df.to_sql(
                "performance_table",
                self.db.get_sqlalchemy_engine(),
                if_exists="append",
                index=False,
            )
            print(
                "[{}] PERF {}%".format(
                    final_object["championName"],
                    final_object["calculated_player_performance"],
                )
            )
        except ValueError:
            print("[DUPLICATE FOUND] {}".format(final_object["match_identifier"]))

    def process_player_performance(self, obj, conn):
        match_identifier = str()
        try:
            match_identifier = obj["info"]["gameId"]
        except KeyError:
            return

        c = conn.cursor()
        c.execute(
            "SELECT EXISTS(SELECT 1 FROM performance_table WHERE match_identifier = %s)",
            (match_identifier,),
        )
        result = c.fetchone()[0]
        if result:
            print("[DUPLICATE FOUND] {}".format(match_identifier))
            return 0

        duration_m = obj["info"]["gameDuration"] / 60

        for participant in obj["info"]["participants"]:
            calculated_performance = self.calculate_player_performance(
                participant, duration_m
            )

            new_object = {
                "match_identifier": match_identifier,
                "duration": duration_m,
                "f1": participant["deaths"] / duration_m,
                "f2": (participant["kills"] + participant["assists"]) / duration_m,
                "f3": participant["champLevel"] / duration_m,
                "f4": participant["totalDamageDealt"] / duration_m,
                "f5": participant["goldEarned"] / duration_m,
                "calculated_player_performance": calculated_performance,
            }

            if new_object["f3"] > 50:
                continue

            second_obj = participant.copy()

            for key in [
                "allInPings",
                "challenges",
                "eligibleForProgression",
                "totalAllyJungleMinionsKilled",
                "totalEnemyJungleMinionsKilled",
                "basicPings",
                "assistMePings",
                "baitPings",
                "commandPings",
                "dangerPings",
                "enemyMissingPings",
                "enemyVisionPings",
                "getBackPings",
                "holdPings",
                "needVisionPings",
                "onMyWayPings",
                "pushPings",
                "visionClearedPings",
                "perks",
            ]:
                try:
                    del second_obj[key]
                except KeyError:
                    pass

            final_object = second_obj | new_object

            self.insert_performance_data(final_object)

        return 1

# Data extraction helper functions
def extract_frame_data(frame, participant_id):
    participant_frame = frame.get("participantFrames").get(str(participant_id))
    if not participant_frame:
        return None

    data = {
        "timestamp": frame.get("timestamp"),
        "participantId": participant_frame.get("participantId"),
        "level": participant_frame.get("level"),
        "xp": participant_frame.get("xp"),
        "totalGold": participant_frame.get("totalGold"),
        "minionsKilled": participant_frame.get("minionsKilled"),
        "jungleMinionsKilled": participant_frame.get("jungleMinionsKilled"),
        "timeEnemySpentControlled": participant_frame.get(
            "timeEnemySpentControlled"
        ),
    }

    champion_stats = participant_frame.get("championStats")
    if champion_stats:
        data.update(
            {
                "abilityPower": champion_stats.get("abilityPower"),
                "armor": champion_stats.get("armor"),
                "attackDamage": champion_stats.get("attackDamage"),
                "attackSpeed": champion_stats.get("attackSpeed"),
                "health": champion_stats.get("health"),
                "healthMax": champion_stats.get("healthMax"),
                "healthRegen": champion_stats.get("healthRegen"),
                "magicResist": champion_stats.get("magicResist"),
                "movementSpeed": champion_stats.get("movementSpeed"),
                "power": champion_stats.get("power"),
                "powerMax": champion_stats.get("powerMax"),
                "powerRegen": champion_stats.get("powerRegen"),
            }
        )

    damage_stats = participant_frame.get("damageStats")
    if damage_stats:
        data.update(
            {
                "totalDamageDealt": damage_stats.get("totalDamageDone"),
                "totalDamageTaken": damage_stats.get("totalDamageTaken"),
            }
        )

    return data


def build_final_object(json_object):
    all_frames = []

    try:
        match_id = json_object.get("metadata").get("matchId")
        winner = (
            json_object.get("info")
            .get("frames")[-1]
            .get("events")[-1]
            .get("winningTeam")
        )
    except AttributeError:
        print(
            "{} [DBG] ERR MATCH_ID RETRIEVAL: {}".format(
                time.strftime("%Y-%m-%d %H:%M"), json_object
            )
        )
        return None

    for frame in json_object.get("info").get("frames"):
        for participant_id in range(1, 11):
            frame_data = extract_frame_data(frame, participant_id)
            if frame_data:
                frame_data["identifier"] = f"{match_id}_{participant_id}"
                frame_data["winner"] = (
                    1
                    if participant_id in (1, 2, 3, 4, 5) and winner == 100 or participant_id not in (1, 2, 3, 4, 5) and winner == 200
                    else 0
                )
                all_frames.append(frame_data)

    return all_frames


def build_final_object_liveclient(json_object):
    all_frames = []

    try:
        match_id = json_object.get("metadata").get("matchId")
        winner = (
            json_object.get("info")
            .get("frames")[-1]
            .get("events")[-1]
            .get("winningTeam")
        )
    except AttributeError:
        print(
            "{} [DBG] ERR MATCH_ID RETRIEVAL: {}".format(
                time.strftime("%Y-%m-%d %H:%M"), json_object
            )
        )
        return None

    for frame in json_object.get("info").get("frames"):
        for participant_id in range(1, 11):
            frame_data = extract_frame_data(frame, participant_id)
            if frame_data:
                frame_data["identifier"] = f"{match_id}_{participant_id}"
                frame_data["winner"] = (
                    1
                    if participant_id in (1, 2, 3, 4, 5) and winner == 100 or participant_id not in (1, 2, 3, 4, 5) and winner == 200
                    else 0
                )
                # Add any live client specific data extraction here
                all_frames.append(frame_data)

    return all_frames


# Background task to populate the database
async def populate_database():
    riot_api = RiotAPI(db)
    for region in riot_api.request_regions:
        for queue in ["RANKED_SOLO_5x5"]:
            riot_api.get_top_players(region, queue, db)


# Lifespan event handler to trigger the background task
async def lifespan(app: FastAPI):
    background_tasks = BackgroundTasks()
    background_tasks.add_task(populate_database)


# API endpoints
@app.get("/summoner/{summoner_name}")
async def get_summoner_info(summoner_name: str, region: str = "na1"):
    try:
        riot_api = RiotAPI(db)
        summoner_info = riot_api.get_summoner_information(summoner_name, region)
        return summoner_info
    except Exception as e:
        return {"error": f"Error retrieving summoner information: {e}"}


@app.get("/champion_mastery/{puuid}")
async def get_champion_mastery(puuid: str, region: str = "na1"):
    try:
        riot_api = RiotAPI(db)
        champion_mastery = riot_api.get_champion_mastery(puuid, region)
        return champion_mastery
    except Exception as e:
        return {"error": f"Error retrieving champion mastery: {e}"}


@app.get("/match_list/{puuid}")
async def get_match_list(
    puuid: str, num_matches: int = 10, queue_type: str = "ranked", region: str = "americas"
):
    try:
        riot_api = RiotAPI(db)
        match_list = riot_api.get_match_ids(puuid, num_matches, queue_type, region)
        return match_list
    except Exception as e:
        return {"error": f"Error retrieving match list: {e}"}


@app.get("/match_detail/{match_id}")
async def get_match_detail(match_id: str):
  try:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM match_detail WHERE match_id = %s", (match_id,))
    match_detail = cursor.fetchone()
    cursor.close()
    return match_detail
  except Exception as e:
    return {"error": f"Error retrieving match detail: {e}"}


@app.post("/performance")
async def calculate_performance(match_id: str):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM match_detail WHERE match_id = %s", (match_id,))
        match_detail = cursor.fetchone()
        if match_detail:
            performance_calculator = ProcessPerformance(cursor)
            performance_data = performance_calculator.process_player_performance(
                match_detail[0], db
            )
            cursor.close()
            return performance_data
    except Exception as e:
        return {"error": f"Error retrieving match detail: {e}"}



@app.get("/")
def home():
    return {"message": "Welcome to the Esports Playmaker"}


@app.get("/logo.png")
async def plugin_logo():
    return FileResponse("logo.png", media_type="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("ai-plugin.json", "r") as f:
        json_content = f.read()
    return Response(content=json_content, media_type="application/json")


@app.get("/openapi.yaml")
async def openapi_spec(request: Request):
    host = request.client.host if request.client else "localhost"
    with open("openapi.yaml", "r") as f:
        yaml_content = f.read()
    yaml_content = yaml_content.replace("PLUGIN_HOSTNAME", f"https://{host}")
    return Response(content=yaml_content, media_type="application/yaml")


# Data mining function
def data_mine(db, mode):
    api = RiotAPI(db)
    if mode == "player_list":
        api.player_list()
    elif mode == "match_list":
        api.match_list()
    elif mode == "match_download_standard":
        api.match_download_standard(db)
    elif mode == "match_download_detail":
        api.match_download_detail(db)
    else:
        api.player_list()
        api.match_list()
        api.match_download_standard(db)
        api.match_download_detail(db)


# Main function
def main(mode):
    db = Database()
    db.run_init_db()
    data_mine(db, mode)


if __name__ == "__main__":
    mode = input("Enter mode (player_list/match_list): ")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    main(mode)
