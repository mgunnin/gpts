import datetime
import os
import random
import time

import pandas as pd
import psycopg2
import requests

riot_api_key = os.getenv("RIOT_API_KEY")

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
        """
        Retrieves the champion mastery information for a given summoner.

        This method fetches the champion mastery details for the specified encrypted summoner ID from the Riot Games API. It constructs a request URL using the provided `request_region` and `puuid`, sends a GET request to the Riot Games API, and processes the response.

        If the request is successful (HTTP status code 200), it prints the response JSON to the console, along with the current timestamp. It then reads the champion IDs from a CSV file, matches them with the champion IDs in the response, and prints detailed mastery information for each champion, including the champion name, mastery level, total mastery points, last time played, points until next mastery level, whether a chest has been granted, and tokens earned.

        If the request fails, it prints an error message with the HTTP status code.

        Parameters:
        - puuid (str): The encrypted summoner ID for which to retrieve champion mastery information.
        - request_region (str): The region from which to request the data. Must be one of the regions specified in `self.request_regions`.

        Returns:
        None. The function prints the champion mastery information to the console.
        """
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
                    datetime.datetime.fromtimestamp(i.get("lastPlayTime") / 1000).strftime(
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


    def get_summoner_leagues(self, summonerId, region):
        assert region in self.request_regions
        request_url = (
            "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(
                region, summonerId
            )
        )

        response = requests.get(request_url, headers=self.headers)
        if response.status_code == 200:
            print("{} {}".format(time.strftime("%Y-%m-%d %H:%M"), response.json()))
        else:
            print(
                "{} Request error (@get_summoner_leagues). HTTP code {}".format(
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
                db.execute_raw(insert_query, (
                    player['summonerId'], player['summonerName'], player['leaguePoints'],
                    player['rank'], player['wins'], player['losses'], player['veteran'],
                    player['inactive'], player['freshBlood'], player['hotStreak'],
                    player['tier'], player['request_region'], player['queue']
                ))
                print("[INS]: {}".format(player["summonerName"]))
            except psycopg2.IntegrityError:
                continue

        # for x in total_users_to_insert:
        #     df = pd.DataFrame(x, index=[0])

        #     try:
        #         df.to_sql("player_table", db.get_connection(), if_exists="append", index=False, method="multi")
        #         print("[INS]: {}".format(x["summonerName"]))
        #     except ValueError:
        #         print("[DUP]: {}".format(x["summonerName"]))
        #         continue
        #     except psycopg2.IntegrityError:
        #         print("[DUP]: {}".format(x["summonerName"]))
        #         continue


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
                    db.execute("INSERT INTO matchups VALUES (?)", (to_insert_obj,))
                except psycopg2.IntegrityError:
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
                    diff.to_sql("match_table", self.db.get_connection(), if_exists="append", index=False)
                    print(
                        "[{}][ADD] +{}".format(time.strftime("%Y-%m-%d %H:%M"), len(diff))
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
                    db.execute("UPDATE match SET processed_5v5 = 1 WHERE key = ?", (x[0],))
                except psycopg2.IntegrityError as e:
                    print(
                        "[{}][DUP]: {} {}".format(
                            time.strftime("%Y-%m-%d %H:%M"), x[0], e
                        )
                    )
                    continue
