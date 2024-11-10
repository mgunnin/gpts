import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            print("Database connection established.")
        except Exception as e:
            print(f"Failed to connect to the database. Error: {e}")

    def execute_query(self, query, params=None, fetch=False):
        """Execute a given SQL query with optional parameters."""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                self.conn.commit()
        except Exception as e:
            print(f"Failed to execute query. Error: {e}")
            self.conn.rollback()

    def create_tables(self):
        """Create tables in the database if they do not already exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS summoners (
                id SERIAL PRIMARY KEY,
                summoner_name VARCHAR(255) NOT NULL,
                region VARCHAR(50) NOT NULL,
                puuid VARCHAR(78) NOT NULL,
                profile_icon_id INT,
                summoner_level BIGINT,
                UNIQUE(summoner_name, region)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS champion_mastery (
                id SERIAL PRIMARY KEY,
                summoner_id INT REFERENCES summoners(id),
                champion_id INT NOT NULL,
                mastery_level INT,
                mastery_points INT,
                UNIQUE(summoner_id, champion_id)
            );
            """,
            # Add more table creation queries as needed
        ]
        for query in queries:
            self.execute_query(query)

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")


# Example usage
if __name__ == "__main__":
    db = Database()
    db.connect()
    db.create_tables()
    db.close()
