import sqlite3

import cassiopeia as cass


def get_summoner_details(summoner_name, region):
    summoner = cass.get_summoner(name=summoner_name, region=region)
    return {
        "accountId": summoner.account_id,
        "puuid": summoner.puuid,
        "profileIconID": summoner.profile_icon.id,
    }


def update_summoner_details_in_db(summoner_name, region, details):
    with sqlite3.connect("lol_summoner.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE top_champion_players
            SET accountId = ?, puuid = ?, profileIconID = ?
            WHERE summoner_name = ? AND region = ?
            """,
            (
                details["accountId"],
                details["puuid"],
                details["profileIconID"],
                summoner_name,
                region,
            ),
        )
        conn.commit()
