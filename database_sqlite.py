import sqlite3
import time

import pandas as pd
from rich import print


class Database:

    def __init__(self, database_path):
        self.database_path = database_path


    def execute(self, query, params=None):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            return cursor


    def get_connection(self):
        return sqlite3.connect(self.database_path)


    def run_init_db(self):
        conn = sqlite3.connect("lol_gpt_v3.db")

        definition = "summonerId REAL PRIMARY KEY, summonerName REAL, leaguePoints REAL, rank REAL, wins REAL, losses REAL, veteran REAL, inactive REAL, freshBlood REAL, hotStreak REAL, tier REAL, request_region REAL, queue REAL"
        conn.execute(f"CREATE TABLE IF NOT EXISTS player_table ({definition})")

        definition = "match_id REAL PRIMARY KEY"
        conn.execute(f"CREATE TABLE IF NOT EXISTS match_table ({definition})")

        definition = "assists REAL, baronKills REAL, bountyLevel REAL, champExperience REAL, champLevel REAL, championId REAL, championName TEXT, championTransform REAL, consumablesPurchased REAL, damageDealtToBuildings REAL, damageDealtToObjectives REAL, damageDealtToTurrets REAL, damageSelfMitigated REAL, deaths REAL, detectorWardsPlaced REAL, doubleKills REAL, dragonKills REAL, firstBloodAssist REAL, firstBloodKill REAL, firstTowerAssist REAL, firstTowerKill REAL, gameEndedInEarlySurrender REAL, gameEndedInSurrender REAL, goldEarned REAL, goldSpent REAL, individualPosition TEXT, inhibitorKills REAL, inhibitorTakedowns REAL, inhibitorsLost REAL, item0 REAL, item1 REAL, item2 REAL, item3 REAL, item4 REAL, item5 REAL, item6 REAL, itemsPurchased REAL, killingSprees REAL, kills REAL, lane TEXT, largestCriticalStrike REAL, largestKillingSpree REAL, largestMultiKill REAL, longestTimeSpentLiving REAL, magicDamageDealt REAL, magicDamageDealtToChampions REAL, magicDamageTaken REAL, neutralMinionsKilled REAL, nexusKills REAL, nexusLost REAL, nexusTakedowns REAL, objectivesStolen REAL, objectivesStolenAssists REAL, participantId REAL, pentaKills REAL, physicalDamageDealt REAL, physicalDamageDealtToChampions REAL, physicalDamageTaken REAL, profileIcon REAL, puuid TEXT, quadraKills REAL, riotIdName TEXT, riotIdTagline TEXT, role TEXT, sightWardsBoughtInGame REAL, spell1Casts REAL, spell2Casts REAL, spell3Casts REAL, spell4Casts REAL, summoner1Casts REAL, summoner1Id REAL, summoner2Casts REAL, summoner2Id REAL, summonerId TEXT, summonerLevel REAL, summonerName TEXT, teamEarlySurrendered REAL, teamId REAL, teamPosition TEXT, timeCCingOthers REAL, timePlayed REAL, totalDamageDealt REAL, totalDamageDealtToChampions REAL, totalDamageShieldedOnTeammates REAL, totalDamageTaken REAL, totalHeal REAL, totalHealsOnTeammates REAL, totalMinionsKilled REAL, totalTimeCCDealt REAL, totalTimeSpentDead REAL, totalUnitsHealed REAL, tripleKills REAL, trueDamageDealt REAL, trueDamageDealtToChampions REAL, trueDamageTaken REAL, turretKills REAL, turretTakedowns REAL, turretsLost REAL, unrealKills REAL, visionScore REAL, visionWardsBoughtInGame REAL, wardsKilled REAL, wardsPlaced REAL, win REAL, match_identifier REAL, duration REAL, f1 REAL, f2 REAL, f3 REAL, f4 REAL, f5 REAL, calculated_player_performance REAL"
        conn.execute(f"CREATE TABLE IF NOT EXISTS performance_table ({definition})")

        definition = "match_id TEXT PRIMARY KEY, game_duration INTEGER, winning_team INTEGER, participants TEXT"
        conn.execute(f"CREATE TABLE IF NOT EXISTS match_detail ({definition})")

        conn.commit()
        conn.close()


    def change_column_value_by_key(self, table_name, column_name, column_value, key):
        connection = self.get_connection()
        cursor = connection.cursor()
        update_statement = f"UPDATE {table_name} SET {column_name} = ? WHERE key_column = ?"
        cursor.execute(update_statement, (column_value, key))
        connection.commit()
        print(
            "{} [DBG] UPDATE BIT {}: {}".format(
                time.strftime("%Y-%m-%d %H:%M"),
                column_name,
                column_value,
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
                time.strftime("%Y-%m-%d %H:%M"),
                len(matches),
            )
        )

        for doc in matches:
            content = doc[0]
            built_object = build_final_object(content)
            if built_object:
                for x in built_object:
                    try:
                        insert_query = "INSERT INTO predictor VALUES (?)"
                        cursor.execute(insert_query, (x,))
                        print(
                            "{} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"),
                                doc[0].get("metadata").get("matchId"),
                            )
                        )
                        update_query = "UPDATE match_detail SET classifier_processed = 1 WHERE key = ?"
                        cursor.execute(update_query, (doc[0],))
                    except sqlite3.IntegrityError as e:
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
                time.strftime("%Y-%m-%d %H:%M"),
                len(matches),
            )
        )

        for doc in matches:
            content = doc[0]
            built_object = build_final_object_liveclient(content)
            if built_object:
                for x in built_object:
                    try:
                        insert_query = "INSERT INTO predictor_liveclient VALUES (?)"
                        cursor.execute(insert_query, (x,))
                        print(doc[0].get("metadata").get("matchId"))
                        update_query = "UPDATE match_detail SET classifier_processed_liveclient = 1 WHERE key = ?"
                        cursor.execute(update_query, (doc[0],))
                    except sqlite3.IntegrityError as e:
                        print(
                            "[{}][DUP]: {} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"), doc[0], e
                            )
                        )
                        continue
        connection.commit()
        connection.close()


class ProcessPerformance:
    def calculate_player_performance(self, participant_data, duration_m):
        deaths_per_min = participant_data["deaths"] / duration_m
        k_a_per_min = (participant_data["kills"] + participant_data["assists"]) / duration_m
        level_per_min = participant_data["champLevel"] / duration_m
        total_damage_per_min = participant_data["totalDamageDealt"] / duration_m
        gold_per_min = participant_data["goldEarned"] / duration_m

        calculated_player_performance = (
            0.336 - (1.437 * deaths_per_min) + (0.000117 * gold_per_min) + (0.443 * k_a_per_min) + (0.264 * level_per_min) + (0.000013 * total_damage_per_min)
        )
        return round((calculated_player_performance * 100), 2)


    def insert_performance_data(self, final_object, conn):
        df = pd.DataFrame(final_object, index=[0])
        try:
            df.to_sql("performance_table", conn, if_exists="append", index=False)
            print(
                "[{}] PERF {}%".format(
                    final_object["championName"], final_object["calculated_player_performance"]
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
            "SELECT EXISTS(SELECT 1 FROM performance_table WHERE match_identifier = ?)",
            (match_identifier,),
        )
        result = c.fetchone()[0]
        if result:
            print("[DUPLICATE FOUND] {}".format(match_identifier))
            return 0

        duration_m = obj["info"]["gameDuration"] / 60

        for participant in obj["info"]["participants"]:
            calculated_performance = self.calculate_player_performance(participant, duration_m)

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

            second_obj = participant.copy()  # Create a copy to avoid modifying original data

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

            self.insert_performance_data(final_object, conn)

        return 1

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
        "timeEnemySpentControlled": participant_frame.get("timeEnemySpentControlled"),
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

    # Additional data extraction (example)
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
      winner = json_object.get("info").get("frames")[-1].get("events")[-1].get("winningTeam")
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
              frame_data["winner"] = 1 if participant_id in (1, 2, 3, 4, 5) and winner == 100 or participant_id not in (1, 2, 3, 4, 5) and winner == 200 else 0
              all_frames.append(frame_data)

  return all_frames


def build_final_object_liveclient(json_object):
  all_frames = []

  try:
      match_id = json_object.get("metadata").get("matchId")
      winner = json_object.get("info").get("frames")[-1].get("events")[-1].get("winningTeam")
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
              frame_data["winner"] = 1 if participant_id in (1, 2, 3, 4, 5) and winner == 100 or participant_id not in (1, 2, 3, 4, 5) and winner == 200 else 0
# Add any live client specific data extraction here
              all_frames.append(frame_data)

  return all_frames
