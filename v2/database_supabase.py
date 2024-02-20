import os
import time

from supabase import Client, create_client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class Database:

    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def run_init_db(self):
        player_table_definition = {
            "summonerId": "double precision primary key",
            "summonerName": "text",
            "leaguePoints": "double precision",
            "rank": "text",
            "wins": "double precision",
            "losses": "double precision",
            "veteran": "boolean",
            "inactive": "boolean",
            "freshBlood": "boolean",
            "hotStreak": "boolean",
            "tier": "text",
            "request_region": "text",
            "queue": "text"
        }
        self.supabase.table("player_table").create(player_table_definition, if_not_exists=True)

        match_table_definition = {
            "match_id": "double precision primary key"
        }
        self.supabase.table("match_table").create(match_table_definition, if_not_exists=True)

        performance_table_definition = {
            # Add all the columns as per the original definition
            # Example:
            "assists": "double precision",
            "baronKills": "double precision",
            # ... add all other columns as needed
        }
        self.supabase.table("performance_table").create(performance_table_definition, if_not_exists=True)

    def change_column_value_by_key(self, table_name: str, column_name: str, column_value, key):
        update_statement = self.supabase.table(table_name).update({column_name: column_value}).eq('key_column', key)
        result = update_statement.execute()
        print(
            "{} [DBG] UPDATE BIT {}: {}".format(
                time.strftime("%Y-%m-%d %H:%M"),
                column_name,
                column_value,
            )
        )

    def process_predictor(self):
        matches = self.supabase.table("match_detail").select("*").eq('classifier_processed', False).execute()
        print(
            "{} Total match_detail documents (to process): {}".format(
                time.strftime("%Y-%m-%d %H:%M"),
                len(matches.data),
            )
        )

        for doc in matches.data:
            content = doc
            built_object = self.build_final_object(content)  # Assuming build_final_object is implemented elsewhere
            if built_object:
                for x in built_object:
                    try:
                        insert_result = self.supabase.table("predictor").insert(x).execute()
                        print(
                            "{} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"),
                                doc.get("metadata").get("matchId"),
                            )
                        )
                        update_result = self.supabase.table("match_detail").update({"classifier_processed": True}).eq('key', doc).execute()
                    except Exception as e:
                        print(
                            "[{}][DUP]: {} {}".format(
                                time.strftime("%Y-%m-%d %H:%M"), doc, e
                            )
                        )
                        continue
