import time

from database import Database
from riot_api_wrapper import RiotAPIWrapper

# List of regions to populate data from
REGIONS = ["na1"]


def populate_summoner_data(api_wrapper, db, region):
    """Populate the database with summoner data."""
    # Example summoner names for demonstration purposes
    summoner_names = ["gameb0x"]

    for name in summoner_names:
        summoner_info = api_wrapper.get_summoner_by_name(region, name)
        if summoner_info:
            db.execute_query(
                """
                INSERT INTO summoners (summoner_name, region, profile_icon_id, summoner_level, puuid)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT (summoner_name, region) DO NOTHING;
                """,
                (
                    summoner_info["name"],
                    region,
                    summoner_info["profileIconId"],
                    summoner_info["summonerLevel"],
                    summoner_info["puuid"],
                    summoner_info["summonerLevel"],
                ),
            )


def populate_champion_mastery(api_wrapper, db, region):
    """Populate the database with champion mastery data."""
    summoners = db.execute_query(
        "SELECT id, summoner_name, puuid FROM summoners WHERE region = %s;",
        (region,),
        fetch=True,
    )

    for summoner in summoners:
        mastery_data = api_wrapper.get_champion_mastery(region, summoner["puuid"])
        if mastery_data:
            for mastery in mastery_data:
                db.execute_query(
                    """
                    INSERT INTO champion_mastery (summoner_id, champion_id, mastery_level, mastery_points)
                    VALUES (%s, %s, %s, %s) ON CONFLICT (summoner_id, champion_id) DO NOTHING;
                    """,
                    (
                        summoner["id"],
                        mastery["championId"],
                        mastery["championLevel"],
                        mastery["championPoints"],
                    ),
                )


def populate_league_info(api_wrapper, db, region):
    """Populate the database with league info data."""
    summoners = db.execute_query(
        "SELECT id, summoner_name FROM summoners WHERE region = %s;",
        (region,),
        fetch=True,
    )

    for summoner in summoners:
        league_info = api_wrapper.get_league_info(region, summoner["summoner_name"])
        if league_info:
            for league in league_info:
                db.execute_query(
                    """
                    INSERT INTO leagues (summoner_id, queue_type, tier, rank, league_points, wins, losses)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (summoner_id, queue_type) DO NOTHING;
                    """,
                    (
                        summoner["id"],
                        league["queueType"],
                        league["tier"],
                        league["rank"],
                        league["leaguePoints"],
                        league["wins"],
                        league["losses"],
                    ),
                )


def populate_match_data(api_wrapper, db, region):
    """Populate the database with match data."""
    summoners = db.execute_query(
        "SELECT id, summoner_name, puuid FROM summoners WHERE region = %s;",
        (region,),
        fetch=True,
    )

    for summoner in summoners:
        match_ids = api_wrapper.get_match_ids(region, summoner["puuid"], count=20)
        for match_id in match_ids:
            match_details = api_wrapper.get_match_details(region, match_id)
            if match_details:
                participants = match_details.get("info", {}).get("participants", [])
                for participant in participants:
                    if participant.get("puuid") == summoner["puuid"]:
                        db.execute_query(
                            """
                            INSERT INTO match_data (summoner_id, match_id, champion_id, queue_id, season_id, timestamp, role, lane)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (summoner_id, match_id) DO NOTHING;
                            """,
                            (
                                summoner["id"],
                                match_id,
                                participant.get("championId"),
                                match_details.get("info", {}).get("queueId"),
                                match_details.get("info", {})
                                .get("gameVersion")
                                .split(".")[0],  # Simplified season extraction
                                match_details.get("info", {}).get("gameCreation"),
                                participant.get("role"),
                                participant.get("lane"),
                            ),
                        )


def main():
    api_wrapper = RiotAPIWrapper()
    db = Database()
    db.connect()

    for region in REGIONS:
        print(f"Populating data for region: {region}")
        populate_summoner_data(api_wrapper, db, region)
        populate_champion_mastery(api_wrapper, db, region)
        # Sleep to respect rate limits
        time.sleep(2)

    db.close()
    print("Data population completed.")


if __name__ == "__main__":
    main()
