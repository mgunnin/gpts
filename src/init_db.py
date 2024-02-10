import sqlite3


def run_init_db():
    """
    Initializes the SQLite database for storing League of Legends player and match data.

    This function is responsible for setting up the initial structure of the SQLite database used to store data related
    to League of Legends players and their match performances. It creates three tables if they do not already exist:
    player_table, match_table, and performance_table.

    The player_table stores basic information about players, including their summoner ID, name, league points, rank,
    wins, losses, and other relevant data. The match_table stores information about individual matches, identified by
    a unique match ID. The performance_table stores detailed performance metrics for players in individual matches,
    including kills, deaths, assists, damage dealt, gold earned, and many other statistics.

    The function connects to the SQLite database 'lol_gpt_v2.db', executes SQL commands to create the tables with the
    appropriate schema if they do not exist, and then closes the connection to the database.

    Note:
    - This function does not return any value.
    - It is assumed that the SQLite database file 'lol_gpt_v2.db' is accessible and writable.
    - The function should be called at the start of the application to ensure the database is initialized before
      any data insertion or query operations are performed.
    """
    # Connect to the database
    conn = sqlite3.connect("lol_gpt_v2.db")

    # conn.execute(f'DROP TABLE PLAYER_TABLE')
    definition = "summonerId REAL PRIMARY KEY, summonerName REAL, leaguePoints REAL, rank REAL, wins REAL, losses REAL, veteran REAL, inactive REAL, freshBlood REAL, hotStreak REAL, tier REAL, request_region REAL, queue REAL"
    conn.execute(f"CREATE TABLE IF NOT EXISTS player_table ({definition})")

    # conn.execute(f'DROP TABLE match_table')
    definition = "match_id REAL PRIMARY KEY"
    conn.execute(f"CREATE TABLE IF NOT EXISTS match_table ({definition})")

    # Create the definition in sql for performance_table, taking all the keys from final_object
    definition = "assists REAL, baronKills REAL, bountyLevel REAL, champExperience REAL, champLevel REAL, championId REAL, championName REAL, championTransform REAL, consumablesPurchased REAL, damageDealtToBuildings REAL, damageDealtToObjectives REAL, damageDealtToTurrets REAL, damageSelfMitigated REAL, deaths REAL, detectorWardsPlaced REAL, doubleKills REAL, dragonKills REAL, firstBloodAssist REAL, firstBloodKill REAL, firstTowerAssist REAL, firstTowerKill REAL, gameEndedInEarlySurrender REAL, gameEndedInSurrender REAL, goldEarned REAL, goldSpent REAL, individualPosition REAL, inhibitorKills REAL, inhibitorTakedowns REAL, inhibitorsLost REAL, item0 REAL, item1 REAL, item2 REAL, item3 REAL, item4 REAL, item5 REAL, item6 REAL, itemsPurchased REAL, killingSprees REAL, kills REAL, lane REAL, largestCriticalStrike REAL, largestKillingSpree REAL, largestMultiKill REAL, longestTimeSpentLiving REAL, magicDamageDealt REAL, magicDamageDealtToChampions REAL, magicDamageTaken REAL, neutralMinionsKilled REAL, nexusKills REAL, nexusLost REAL, nexusTakedowns REAL, objectivesStolen REAL, objectivesStolenAssists REAL, participantId REAL, pentaKills REAL, physicalDamageDealt REAL, physicalDamageDealtToChampions REAL, physicalDamageTaken REAL, profileIcon REAL, puuid REAL, quadraKills REAL, riotIdName REAL, riotIdTagline REAL, role REAL, sightWardsBoughtInGame REAL, spell1Casts REAL, spell2Casts REAL, spell3Casts REAL, spell4Casts REAL, summoner1Casts REAL, summoner1Id REAL, summoner2Casts REAL, summoner2Id REAL, summonerId REAL, summonerLevel REAL, summonerName REAL, teamEarlySurrendered REAL, teamId REAL, teamPosition REAL, timeCCingOthers REAL, timePlayed REAL, totalDamageDealt REAL, totalDamageDealtToChampions REAL, totalDamageShieldedOnTeammates REAL, totalDamageTaken REAL, totalHeal REAL, totalHealsOnTeammates REAL, totalMinionsKilled REAL, totalTimeCCDealt REAL, totalTimeSpentDead REAL, totalUnitsHealed REAL, tripleKills REAL, trueDamageDealt REAL, trueDamageDealtToChampions REAL, trueDamageTaken REAL, turretKills REAL, turretTakedowns REAL, turretsLost REAL, unrealKills REAL, visionScore REAL, visionWardsBoughtInGame REAL, wardsKilled REAL, wardsPlaced REAL, win REAL, match_identifier REAL, duration REAL, f1 REAL, f2 REAL, f3 REAL, f4 REAL, f5 REAL, calculated_player_performance REAL"
    conn.execute(f"CREATE TABLE IF NOT EXISTS performance_table ({definition})")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run_init_db()
