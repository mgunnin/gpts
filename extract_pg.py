import os

import psycopg2
from dotenv import load_dotenv

from database_pg import Database
from riot_api import RiotAPI

conn = psycopg2.connect(
    host=os.environ.get("SUPABASE_URL"),
    port=os.environ.get("SUPABASE_PORT"),
    database=os.environ.get("SUPABASE_DB"),
    user=os.environ.get("SUPABASE_USER"),
    password=os.environ.get("SUPABASE_PW")
)

# cursor = conn.cursor()
# query = "SELECT * FROM match_table"
# cursor.execute(query)
# result_set = cursor.fetchall()
# random.shuffle(result_set)

# df = pd.DataFrame(result_set, columns=["match_id"])

# conn.close()

# currently_limited = 0

# print(df.tail(3))
# print("Dataframe length: {}".format(len(df)))

load_dotenv()

riot_api_key = os.getenv("RIOT_API_KEY")
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": riot_api_key,
}

def data_mine(db, mode):
    api = RiotAPI(db)
    if mode == "player_list":
        api.player_list()
    elif mode == "match_list":
        api.match_list()
    elif mode == "match_download_standard":
        api.match_download_standard(db)
    elif mode == "match_download_detail":
        api.match_download_detail(db)
    else:
        api.player_list()
        api.match_list()
        api.match_download_standard(db)
        api.match_download_detail(db)

def main(mode):
    #db = Database("lol_gpt_v3.db")
    db = Database(conn)
    db.run_init_db()
    data_mine(db, mode)


if __name__ == "__main__":
    mode = input("Enter mode (player_list/match_list): ")
    main(mode)
