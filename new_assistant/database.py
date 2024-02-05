import aiosqlite
from config import CONFIG


async def create_db():
    db_schema = """
    CREATE TABLE IF NOT EXISTS top_champion_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summoner_name TEXT NOT NULL,
        region TEXT NOT NULL,
        puuid TEXT UNIQUE NOT NULL,
        account_id TEXT,
        profile_icon_id INTEGER,
        summoner_level INTEGER,
        summoner_id TEXT,
        UNIQUE(summoner_name, region)
    );
    CREATE TABLE IF NOT EXISTS match_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        puuid TEXT NOT NULL,
        match_id TEXT NOT NULL,
        game_creation INTEGER NOT NULL,
        champion_name TEXT NOT NULL,
        kills INTEGER NOT NULL,
        deaths INTEGER NOT NULL,
        assists INTEGER NOT NULL,
        total_damage_dealt_to_champions INTEGER NOT NULL,
        vision_score INTEGER NOT NULL,
        gold_earned INTEGER NOT NULL,
        total_minions_killed INTEGER NOT NULL,
        role TEXT NOT NULL,
        win BOOLEAN NOT NULL,
        FOREIGN KEY(puuid) REFERENCES top_champion_players(puuid)
    );
    """
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        await db.executescript(db_schema)
        await db.commit()


async def fetch_all_puuids():
    fetch_sql = "SELECT puuid FROM top_champion_players"
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        cursor = await db.execute(fetch_sql)
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def insert_top_champion_players(data):
    insert_sql = """
    INSERT INTO top_champion_players (summoner_name, region, puuid, account_id, profile_icon_id, summoner_level, summoner_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        await db.execute(insert_sql, data)
        await db.commit()


async def insert_match_history(data):
    insert_sql = """
    INSERT INTO match_history (puuid, match_id, game_creation, champion_name, kills, deaths, assists, total_damage_dealt_to_champions, vision_score, gold_earned, total_minions_killed, role, win)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    async with aiosqlite.connect(CONFIG["DB_PATH"]) as db:
        await db.execute(insert_sql, data)
        await db.commit()
