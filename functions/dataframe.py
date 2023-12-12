# Wrapping All Functions Into One
def master_function(
    summoner_name, region, mass_region, NO_GAMES, QUEUE_ID, RIOT_API_KEY
):
    puuid = get_puuid(summoner_name, region, RIOT_API_KEY)
    match_ids = get_match_ids(puuid, mass_region, NO_GAMES, QUEUE_ID, RIOT_API_KEY)
    df = gather_all_data(puuid, match_ids, mass_region, RIOT_API_KEY)
    return df


def find_player_data(match_data, puuid):
    participants = match_data["metadata"]["participants"]
    player_index = participants.index(puuid)
    player_data = match_data["info"]["participants"][player_index]
    return player_data


df = master_function(
    summoner_name, region, mass_region, NO_GAMES, QUEUE_ID, RIOT_API_KEY
)


df

# create a count column
df["count"] = 1

# the "agg" allows us to get the average of every column but sum the count                                       # see?
champ_df = df.groupby("champion").agg(
    {
        "kills": "mean",
        "deaths": "mean",
        "assists": "mean",
        "win": "mean",
        "count": "sum",
    }
)

# we reset in the index so we can still use the "champion" column
champ_df.reset_index(inplace=True)

# we limit it to only champions where you've played 2 or more games
champ_df = champ_df[champ_df["count"] >= 2]

# create a kda column
champ_df["kda"] = (champ_df["kills"] + champ_df["assists"]) / champ_df["deaths"]

# sort the table by KDA, starting from the highest
champ_df = champ_df.sort_values(
    "kda", ascending=False
)  # ascending determines whether it's highest to lowest or vice-versa

# assign the first row and last row to a variable so we can print information about it
best_row = champ_df.iloc[0]  # .iloc[0] simply takes the first row in dataframe
worst_row = champ_df.iloc[-1]  # .iloc[-1] takes the last row in a dataframe

# sort by count instead
champ_df = champ_df.sort_values("count", ascending=False)

# get your most played champ
row = champ_df.iloc[0]

# Assign and format the win rate
win_rate = row["win"]
win_rate = str(round(win_rate * 100, 1)) + "%"

# Sort by highest kills in a game (note, not using the champ_df groupby anymore but the raw data)
highest_kills = df.sort_values("kills", ascending=False)
row = highest_kills.iloc[0]
