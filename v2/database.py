import sqlite3
import time

from rich import print


class Database:

    def __init__(self, database_path):
        self.database_path = database_path


    def get_connection(self):
        return sqlite3.connect(self.database_path)


    def run_init_db(self):
        """
        Initializes the SQLite database for storing League of Legends player and match data.

        This function is responsible for setting up the initial structure of the SQLite database used to store data related
        to League of Legends players and their match performances. It creates three tables if they do not already exist:
        player_table, match_table, and performance_table.

        The player_table stores basic information about players, including their summoner ID, name, league points, rank,
        wins, losses, and other relevant data. The match_table stores information about individual matches, identified by
        a unique match ID. The performance_table stores detailed performance metrics for players in individual matches,
        including kills, deaths, assists, damage dealt, gold earned, and many other statistics.

        The function connects to the SQLite database 'lol_gpt_v3.db', executes SQL commands to create the tables with the
        appropriate schema if they do not exist, and then closes the connection to the database.

        Note:
        - This function does not return any value.
        - It is assumed that the SQLite database file 'lol_gpt_v3.db' is accessible and writable.
        - The function should be called at the start of the application to ensure the database is initialized before
        any data insertion or query operations are performed.
        """
        # Connect to the database
        conn = sqlite3.connect("lol_gpt_v3.db")

        # conn.execute(f'DROP TABLE PLAYER_TABLE')
        definition = "summonerId REAL PRIMARY KEY, summonerName REAL, leaguePoints REAL, rank REAL, wins REAL, losses REAL, veteran REAL, inactive REAL, freshBlood REAL, hotStreak REAL, tier REAL, request_region REAL, queue REAL"
        conn.execute(f"CREATE TABLE IF NOT EXISTS player_table ({definition})")

        # conn.execute(f'DROP TABLE match_table')
        definition = "match_id REAL PRIMARY KEY"
        conn.execute(f"CREATE TABLE IF NOT EXISTS match_table ({definition})")

        # Create the definition in sql for performance_table, taking all the keys from final_object
        definition = "assists REAL, baronKills REAL, bountyLevel REAL, champExperience REAL, champLevel REAL, championId REAL, championName REAL, championTransform REAL, consumablesPurchased REAL, damageDealtToBuildings REAL, damageDealtToObjectives REAL, damageDealtToTurrets REAL, damageSelfMitigated REAL, deaths REAL, detectorWardsPlaced REAL, doubleKills REAL, dragonKills REAL, firstBloodAssist REAL, firstBloodKill REAL, firstTowerAssist REAL, firstTowerKill REAL, gameEndedInEarlySurrender REAL, gameEndedInSurrender REAL, goldEarned REAL, goldSpent REAL, individualPosition REAL, inhibitorKills REAL, inhibitorTakedowns REAL, inhibitorsLost REAL, item0 REAL, item1 REAL, item2 REAL, item3 REAL, item4 REAL, item5 REAL, item6 REAL, itemsPurchased REAL, killingSprees REAL, kills REAL, lane REAL, largestCriticalStrike REAL, largestKillingSpree REAL, largestMultiKill REAL, longestTimeSpentLiving REAL, magicDamageDealt REAL, magicDamageDealtToChampions REAL, magicDamageTaken REAL, neutralMinionsKilled REAL, nexusKills REAL, nexusLost REAL, nexusTakedowns REAL, objectivesStolen REAL, objectivesStolenAssists REAL, participantId REAL, pentaKills REAL, physicalDamageDealt REAL, physicalDamageDealtToChampions REAL, physicalDamageTaken REAL, profileIcon REAL, puuid REAL, quadraKills REAL, riotIdName REAL, riotIdTagline REAL, role REAL, sightWardsBoughtInGame REAL, spell1Casts REAL, spell2Casts REAL, spell3Casts REAL, spell4Casts REAL, summoner1Casts REAL, summoner1Id REAL, summoner2Casts REAL, summoner2Id REAL, summonerId REAL, summonerLevel REAL, summonerName REAL, teamEarlySurrendered REAL, teamId REAL, teamPosition REAL, timeCCingOthers REAL, timePlayed REAL, totalDamageDealt REAL, totalDamageDealtToChampions REAL, totalDamageShieldedOnTeammates REAL, totalDamageTaken REAL, totalHeal REAL, totalHealsOnTeammates REAL, totalMinionsKilled REAL, totalTimeCCDealt REAL, totalTimeSpentDead REAL, totalUnitsHealed REAL, tripleKills REAL, trueDamageDealt REAL, trueDamageDealtToChampions REAL, trueDamageTaken REAL, turretKills REAL, turretTakedowns REAL, turretsLost REAL, unrealKills REAL, visionScore REAL, visionWardsBoughtInGame REAL, wardsKilled REAL, wardsPlaced REAL, win REAL, match_identifier REAL, duration REAL, f1 REAL, f2 REAL, f3 REAL, f4 REAL, f5 REAL, calculated_player_performance REAL"
        conn.execute(f"CREATE TABLE IF NOT EXISTS performance_table ({definition})")

        pass

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


    def build_final_object(self, json_object):
        all_frames = list()

        try:
            match_id = json_object.get("metadata").get("matchId")
        except AttributeError:
            print(
                "{} [DBG] ERR MATCH_ID RETRIEVAL: {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), json_object
                )
            )
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


    def build_final_object_liveclient(self, json_object):
        all_frames = list()
        match_id = str()
        try:
            match_id = json_object.get("metadata").get("matchId")
        except AttributeError:
            print(
                "{} [DBG] ERR MATCH_ID RETRIEVAL: {}".format(
                    time.strftime("%Y-%m-%d %H:%M"), json_object
                )
            )
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
            built_object = self.build_final_object(content)
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
            built_object = self.build_final_object_liveclient(content)
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
