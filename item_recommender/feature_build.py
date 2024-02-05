import json
import logging
import sqlite3

import pandas as pd


def load_data(db="data/matches.db", table="player_items_champions"):
    """Load data from database and return as pandas dataframe"""
    conn = sqlite3.connect(db)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df


def create_champ_df(
    version_filepath="data/version.json",
    feature_filepath="data/champ_matrix_filled.csv",
    save=True,
):
    """Create dataframe of champions and their attributes"""

    # open json file, get version
    f = open(version_filepath)
    version = json.load(f)[0]

    # open json file, get data
    f = open(f"data/{version}/{version}/data/en_US/champion.json", encoding="utf8")
    champ_data = json.load(f)["data"]

    # define features we want to keep
    features = ["version", "id", "key", "name", "info", "tags"]

    # create a list of dictionaries, each dictionary is a champion
    champ_list = []
    for key, value in champ_data.items():
        champ_dict = {}
        temp = value
        for feature in features:
            champ_dict[feature] = temp[feature]
            if feature == "info":
                for key, value in value[feature].items():
                    champ_dict[key] = value
        champ_list.append(champ_dict)

    # create dataframe from list of dictionaries
    champ_df = pd.DataFrame().from_dict(champ_list)
    champ_df = champ_df.drop(labels=["info"], axis=1)

    # load in manually-defined feature csv and join with current dataframe
    champ_features = [
        "version",
        "id",
        "mobility",
        "poke",
        "sustained",
        "burst",
        "engage",
        "disengage",
        "healing",
    ]
    try:
        temp_df = pd.read_csv("data/champ_matrix_filled.csv")
    except:
        print(
            "Self-annotated data not found at data/champ_matrix_filled.csv. Create this file using the instructions from the github repository, or download it."
        )
        raise

    # return any champions present in local datadragon files but not in our manually-created feature matrix
    new_champs = list(set(champ_df["id"]).difference(set(temp_df["id"])))
    changelist = {}
    for champ in new_champs:
        champ_entry = pd.DataFrame({"id": [champ], "version": [version]})
        print(champ_entry)
        temp_df = pd.concat([temp_df, champ_entry], ignore_index=True)

        print(
            f"New champion {champ} needs features added! For each prompt, provide a value from 0-3 for the character, then press enter.\n"
        )
        champ_attr = {}
        for f in champ_features[2:]:
            print(f"{f}: ")
            champ_attr[f] = int(input())  # TODO: Add input validation
            temp_df.loc[temp_df["id"] == champ, f] = champ_attr[f]

        changelist[champ] = champ_attr

        if save:
            temp_df.to_csv("data/champ_matrix_filled.csv", index=False)

    temp_df = temp_df[champ_features]

    champ_df = champ_df.merge(temp_df, how="left", on="id")
    champ_df["version"] = champ_df["version_x"]
    champ_df = champ_df.drop(labels=["version_x", "version_y"], axis=1)

    # add new champ features
    for champ, attr in changelist.items():
        for key, value in attr.items():
            champ_df.loc[champ_df["id"] == champ, key] = value
        print(f"Updated entry for {champ}!")

    # one hot encode the tags column, and sum to get back to original row shape
    temp_df = pd.get_dummies(champ_df["tags"].explode(), columns=["tags"])
    temp_df = temp_df.groupby(temp_df.index).sum()

    # merge temp_df with champ_df
    champ_df = pd.concat([champ_df, temp_df], axis=1)

    # transform key column to int
    champ_df["key"] = champ_df["key"].astype(int)

    # drop tags and difficulty columns
    champ_df = champ_df.drop(labels=["tags", "difficulty"], axis=1)

    # move version column back to front
    cols = champ_df.columns.tolist()
    cols.remove("version")
    cols.insert(0, "version")
    champ_df = champ_df[cols]

    if save:
        champ_df.to_csv("data/champ_df.csv", index=False)

    return champ_df


def get_summed_features(df, champ_df):
    """Get summed features for ally and enemy teams"""

    # champ_df indices we want
    cols = champ_df.columns[4:].to_list()

    # create unique for ally and enemy sums
    ally_cols = ["ally_" + x for x in cols]
    enemy_cols = ["enemy_" + x for x in cols]

    # new dataframe to store vals in
    summed_features = pd.DataFrame(columns=ally_cols + enemy_cols)

    for index, row in df.iterrows():
        # enemies list
        enemy_ids = row[21:26].to_list()
        # ally list
        ally_ids = row[26:31].to_list()

        # list of vals to fill
        ally_stats = champ_df[champ_df["key"].isin(ally_ids)].sum()[4:].to_list()
        enemy_stats = champ_df[champ_df["key"].isin(enemy_ids)].sum()[4:].to_list()

        stats = ally_stats + enemy_stats
        summed_features.loc[len(summed_features)] = stats

    # merge with match_ids
    df = pd.concat([df, summed_features], axis=1)

    # create KDA column
    df["kda"] = (df["kills"] + df["assists"]) / df["deaths"]
    df.loc[df["deaths"] == 0, "kda"] = (
        df["kills"] + df["assists"]
    )  # where deaths = 0, set kd_ratio to kills + assists

    # move the kda column to the front
    column_to_move = df.pop("kda")  # remove column
    # insert column at position 10
    df.insert(10, "kda", column_to_move)

    # return dataframe
    return df


def save_to_db(df, db="data/matches.db", name="match_features"):
    conn = sqlite3.connect(db)
    df.to_sql(name, conn, if_exists="append", index=False)
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Loading data...")
    df = load_data()
    logging.info("Creating features...")
    champ_df = create_champ_df()
    df = get_summed_features(df, champ_df)
    logging.info("Saving to database...")
    save_to_db(df)
    logging.info("Great Success!")
