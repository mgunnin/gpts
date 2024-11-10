"""
Reads data from an SQLite database into Pandas DataFrames.

Connects to the database file 'lol_gpt_v2.db' and reads the tables
'performance_table', 'player_table', and 'match_table' into DataFrames.

Exports each DataFrame to a CSV file named after the table.

No data transformation, just extracting the tables from SQL to Pandas.
"""

import sqlite3

import pandas as pd

# Connect to the database
conn = sqlite3.connect("lol_gpt_v2.db")

# Read table from sqlite database
df = pd.read_sql_query("SELECT * FROM performance_table", conn)
print(df.tail())
pd.set_option("display.max_columns", None)
# print(df.iloc[-1]['summonerId'])
print(len(df))

df.to_csv("performance_report.csv", index=True)

df = pd.read_sql_query("SELECT * FROM player_table", conn)

print(df.tail())

print(len(df))

df.to_csv("player_report.csv", index=True)

df = pd.read_sql_query("SELECT * FROM match_table", conn)

print(df.tail())

print(len(df))

df.to_csv("match_report.csv", index=True)

# print(', '.join([f'{key} REAL' for key in final_object.keys()]))
