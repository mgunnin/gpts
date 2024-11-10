import os
import time

import pandas as pd
import psycopg2
from rich import print
from sqlalchemy import create_engine


class Database:

    def __init__(self, database_path):
        self.database_path = database_path

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
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
        )

    def get_sqlalchemy_engine(self):
        database_url = (
            f"postgresql+psycopg2://{os.environ.get('DB_USER')}:"
            f"{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:"
            f"{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
        )
        engine = create_engine(database_url)
        return engine

    def run_init_db(self):
        conn = self.get_connection()
        player_table = """
            CREATE TABLE IF NOT EXISTS player_table (
                summoner_id TEXT PRIMARY KEY,
                summoner_name TEXT,
                league_points INTEGER,
                rank TEXT,
                wins INTEGER,
                losses INTEGER,
                veteran BOOLEAN,
                inactive BOOLEAN,
                fresh_blood BOOLEAN,
                hot_streak BOOLEAN,
                tier TEXT,
                request_region TEXT,
                queue TEXT
            )
        """

        match_table = """
            CREATE TABLE IF NOT EXISTS match_table (
                match_id TEXT PRIMARY KEY
            )
        """

        performance_table = """
            CREATE TABLE IF NOT EXISTS performance_table (
                assists INTEGER,
                baron_kills INTEGER,
                bounty_level INTEGER,
                champ_experience INTEGER,
                champ_level INTEGER,
                champion_id INTEGER,
                champion_name TEXT,
                champion_transform INTEGER,
                consumables_purchased INTEGER,
                damage_dealt_to_buildings INTEGER,
                damage_dealt_to_objectives INTEGER,
                damage_dealt_to_turrets INTEGER,
                damage_self_mitigated INTEGER,
                deaths INTEGER,
                detector_wards_placed INTEGER,
                double_kills INTEGER,
                dragon_kills INTEGER,
                first_blood_assist BOOLEAN,
                first_blood_kill BOOLEAN,
                first_tower_assist BOOLEAN,
                first_tower_kill BOOLEAN,
                game_ended_in_early_surrender BOOLEAN,
                game_ended_in_surrender BOOLEAN,
                gold_earned INTEGER,
                gold_spent INTEGER,
                individual_position TEXT,
                inhibitor_kills INTEGER,
                inhibitor_takedowns INTEGER,
                inhibitors_lost INTEGER,
                item_0 INTEGER,
                item_1 INTEGER,
                item_2 INTEGER,
                item_3 INTEGER,
                item_4 INTEGER,
                item_5 INTEGER,
                item_6 INTEGER,
                items_purchased INTEGER,
                killing_sprees INTEGER,
                kills INTEGER,
                lane TEXT,
                largest_critical_strike INTEGER,
                largest_killing_spree INTEGER,
                largest_multi_kill INTEGER,
                longest_time_spent_living INTEGER,
                magic_damage_dealt INTEGER,
                magic_damage_dealt_to_champions INTEGER,
                magic_damage_taken INTEGER,
                neutral_minions_killed INTEGER,
                nexus_kills INTEGER,
                nexus_lost INTEGER,
                nexus_takedowns INTEGER,
                objectives_stolen INTEGER,
                objectives_stolen_assists INTEGER,
                participant_id INTEGER,
                penta_kills INTEGER,
                physical_damage_dealt INTEGER,
                physical_damage_dealt_to_champions INTEGER,
                physical_damage_taken INTEGER,
                profile_icon INTEGER,
                puuid TEXT,
                quadra_kills INTEGER,
                riot_id_name TEXT,
                riot_id_tagline TEXT,
                role TEXT,
                sight_wards_bought_in_game INTEGER,
                spell_1_casts INTEGER,
                spell_2_casts INTEGER,
                spell_3_casts INTEGER,
                spell_4_casts INTEGER,
                summoner_1_casts INTEGER,
                summoner_1_id INTEGER,
                summoner_2_casts INTEGER,
                summoner_2_id INTEGER,
                summoner_id TEXT,
                summoner_level INTEGER,
                summoner_name TEXT,
                team_early_surrendered BOOLEAN,
                team_id INTEGER,
                team_position TEXT,
                time_ccing_others INTEGER,
                time_played INTEGER,
                total_damage_dealt INTEGER,
                total_damage_dealt_to_champions INTEGER,
                total_damage_shielded_on_teammates INTEGER,
                total_damage_taken INTEGER,
                total_heal INTEGER,
                total_heals_on_teammates INTEGER,
                total_minions_killed INTEGER,
                total_time_cc_dealt INTEGER,
                total_time_spent_dead INTEGER,
                total_units_healed INTEGER,
                triple_kills INTEGER,
                true_damage_dealt INTEGER,
                true_damage_dealt_to_champions INTEGER,
                true_damage_taken INTEGER,
                turret_kills INTEGER,
                turret_takedowns INTEGER,
                turrets_lost INTEGER,
                unreal_kills INTEGER,
                vision_score INTEGER,
                vision_wards_bought_in_game INTEGER,
                wards_killed INTEGER,
                wards_placed INTEGER,
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

        match_detail = """
            CREATE TABLE IF NOT EXISTS match_detail (
                match_id TEXT PRIMARY KEY,
                game_duration INTEGER,
                winning_team INTEGER,
                participants TEXT,
                participant_id INTEGER,
                team_id INTEGER,
                champion_id INTEGER,
                champion_name TEXT,
                champion_transform INTEGER,
                individual_position TEXT,
                lane TEXT,
                role TEXT,
                kills INTEGER,
                deaths INTEGER,
                assists INTEGER,
                total_damage_dealt INTEGER,
                total_damage_dealt_to_champions INTEGER,
                total_damage_taken INTEGER,
                total_heal INTEGER,
                total_minions_killed INTEGER,
                gold_earned INTEGER,
                gold_spent INTEGER,
                turret_kills INTEGER,
                turret_takedowns INTEGER,
                turrets_lost INTEGER,
                inhibitor_kills INTEGER,
                inhibitor_takedowns INTEGER,
                inhibitors_lost INTEGER,
                total_time_spent_dead INTEGER,
                vision_score INTEGER,
                wards_placed INTEGER,
                wards_killed INTEGER,
                first_blood_kill BOOLEAN,
                first_blood_assist BOOLEAN,
                first_tower_kill BOOLEAN,
                first_tower_assist BOOLEAN,
                win BOOLEAN
            )
        """

        top_players = """
            CREATE TABLE IF NOT EXISTS top_players (
                summoner_name TEXT,
                region TEXT,
                tier TEXT,
                division TEXT,
                league_points INTEGER,
                wins INTEGER,
                losses INTEGER,
                veteran BOOLEAN,
                inactive BOOLEAN,
                fresh_blood BOOLEAN,
                hot_streak BOOLEAN,
                queue TEXT
            )
        """

        # Execute table creation queries
        self.execute(player_table)
        self.execute(match_table)
        self.execute(performance_table)
        self.execute(match_detail)
        self.execute(top_players)

        conn.commit()
        conn.close()

    def change_column_value_by_key(self, table_name, column_name, column_value, key):
        """
        Updates the value of a specific column in a table based on a given key.

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column to be updated.
            column_value: The new value to be set for the column.
            key: The key used to identify the row to be updated.

        Returns:
            None
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        update_statement = (
            f"UPDATE {table_name} SET {column_name} = %s WHERE key_column = %s"
        )
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
                        insert_query = "INSERT INTO predictor VALUES (%s)"
                        cursor.execute(insert_query, (x,))
                        print(
                            "{} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"),
                                doc[0].get("metadata").get("matchId"),
                            )
                        )
                        update_query = "UPDATE match_detail SET classifier_processed = 1 WHERE key = %s"
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
                        insert_query = "INSERT INTO predictor_liveclient VALUES (%s)"
                        cursor.execute(insert_query, (x,))
                        print(doc[0].get("metadata").get("matchId"))
                        update_query = "UPDATE match_detail SET classifier_processed_liveclient = 1 WHERE key = %s"
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
            0.336
            - (1.437 * deaths_per_min)
            + (0.000117 * gold_per_min)
            + (0.443 * k_a_per_min)
            + (0.264 * level_per_min)
            + (0.000013 * total_damage_per_min)
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


def extract_frame_data(frame, participant_id):
    """
    Extracts relevant data from a frame for a specific participant.

    Args:
        frame (dict): The frame containing participant data.
        participant_id (int): The ID of the participant.

    Returns:
        dict: A dictionary containing the extracted data for the participant.
              The dictionary includes the following keys:
              - timestamp
              - participantId
              - level
              - xp
              - totalGold
              - minionsKilled
              - jungleMinionsKilled
              - timeEnemySpentControlled
              - abilityPower (optional)
              - armor (optional)
              - attackDamage (optional)
              - attackSpeed (optional)
              - health (optional)
              - healthMax (optional)
              - healthRegen (optional)
              - magicResist (optional)
              - movementSpeed (optional)
              - power (optional)
              - powerMax (optional)
              - powerRegen (optional)
              - totalDamageDealt (optional)
              - totalDamageTaken (optional)
    """
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
                    if participant_id in (1, 2, 3, 4, 5)
                    and winner == 100
                    or participant_id not in (1, 2, 3, 4, 5)
                    and winner == 200
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
                    if participant_id in (1, 2, 3, 4, 5)
                    and winner == 100
                    or participant_id not in (1, 2, 3, 4, 5)
                    and winner == 200
                    else 0
                )
                all_frames.append(frame_data)

    return all_frames
