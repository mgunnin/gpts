import aiosqlite
from config import CONFIG


async def create_db():
    db_schema = """
    CREATE TABLE IF NOT EXISTS top_champion_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summoner_name TEXT,
        region TEXT,
        champion TEXT,
        puuid TEXT UNIQUE,
        account_id TEXT,
        profile_icon_id INTEGER,
        summoner_level INTEGER,
        summoner_id TEXT,
        UNIQUE(account_id)
    );
    CREATE TABLE IF NOT EXISTS match_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT,
        puuid TEXT,
        summoner_name TEXT,
        champion_name TEXT,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        kda REAL,
        total_damage_dealt INTEGER,
        total_damage_taken INTEGER,
        total_healing_done INTEGER,
        total_damage_dealt_to_champions INTEGER,
        total_minions_killed INTEGER,
        vision_score INTEGER,
        gold_earned INTEGER,
        win BOOLEAN,
        FOREIGN KEY(puuid) REFERENCES top_champion_players(puuid)
    );
    """
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        await db.executescript(db_schema)
        await db.commit()


async def puuid_exists(puuid):
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        cursor = await db.execute(
            "SELECT 1 FROM top_champion_players WHERE puuid = ?", (puuid,)
        )
        result = await cursor.fetchone()
        return result is not None


async def fetch_all_puuids():
    fetch_sql = "SELECT puuid FROM top_champion_players"
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        cursor = await db.execute(fetch_sql)
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def insert_top_champion_players(data):
    insert_sql = """
    INSERT INTO top_champion_players (summoner_name, region, champion, puuid, account_id, profile_icon_id, summoner_level, summoner_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        await db.execute(insert_sql, data)
        await db.commit()


async def insert_match_history(match_data):
    insert_sql = """
    INSERT INTO match_history (game_id, puuid, summoner_name, champion_name, kills, deaths, assists, kda, total_damage_dealt, total_damage_taken, total_healing_done, total_damage_dealt_to_champions, total_minions_killed, vision_score, gold_earned, win)
    VALUES (:game_id, :puuid, :summoner_name, :champion_name, :kills, :deaths, :assists, :kda, :total_damage_dealt, :total_damage_taken, :total_healing_done, :total_damage_dealt_to_champions, :total_minions_killed, :vision_score, :gold_earned, :win)
    """
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        await db.execute(insert_sql, match_data)
        await db.commit()
