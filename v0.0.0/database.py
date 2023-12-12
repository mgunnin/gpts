import json
import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, host, port, user, password, db_name):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=db_name
        )
        self.cur = self.conn.cursor()

    def save_player_stats(self, player_name, player_stats):
        # Create table if not exists
        self.cur.execute(
            sql.SQL(
                "CREATE TABLE IF NOT EXISTS {} ("
                "id SERIAL PRIMARY KEY,"
                "player_name VARCHAR(255),"
                "player_stats JSONB"
                ")"
            ).format(sql.Identifier(player_name))
        )

        # Insert player stats into the table
        self.cur.execute(
            sql.SQL(
                "INSERT INTO {} (player_name, player_stats) "
                "VALUES (%s, %s)"
            ).format(sql.Identifier(player_name)),
            (player_name, json.dumps(player_stats))
        )

        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
