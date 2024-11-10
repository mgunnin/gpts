import sqlite3

import pandas as pd

# Initializes database definitions and primary key to avoid inserting duplicates into dataset
# Can also use this file to just test stuff, get visualizations from the db, etc.
# Connect to the database
conn = sqlite3.connect("lol_gpt_v3.db")

# Execute SQL statement to add primary key
results = conn.execute('''SELECT *, MAX(rowid) FROM player_table WHERE summonerName="FOURE7038634357" GROUP BY summonerId''')  
if len(results.fetchall()) > 1:
    conn.execute('''DELETE FROM player_table WHERE rowid NOT IN (SELECT MAX(rowid) FROM player_table GROUP BY summonerId)''')

#conn.execute(f'DROP TABLE PLAYER_TABLE')
definition = 'summonerId REAL PRIMARY KEY, summonerName REAL, leaguePoints REAL, rank REAL, wins REAL, losses REAL, veteran REAL, inactive REAL, freshBlood REAL, hotStreak REAL, tier REAL, request_region REAL, queue REAL'
conn.execute(f'CREATE TABLE IF NOT EXISTS player_table ({definition})')

#conn.execute(f'DROP TABLE match_table')
definition = 'match_id REAL PRIMARY KEY'
conn.execute(f'CREATE TABLE IF NOT EXISTS match_table ({definition})')
