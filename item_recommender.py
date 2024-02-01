import argparse
import json
import os
import platform
import pwd

import numpy as np
import pandas as pd
import requests
from feature_build import load_data
from scipy.spatial import KDTree

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()


def normalize_df(df):
    """Normalize the dataframe, keep min and max stored for normalizing new entries"""
    # normalize our columns
    df_scaled = df.copy()
    # store max, min in dict
    norm_dict = {}
    for column in df.columns[31:]:
        norm_dict[column] = [df_scaled[column].max(), df_scaled[column].min()]
        df_scaled[column] = (df_scaled[column] - df_scaled[column].min()) / (
            df_scaled[column].max() - df_scaled[column].min()
        )

    return df_scaled, norm_dict


def create_trees(df):
    """Create KDTree for each champion"""
    # create a dictionary to store the KDTrees for each champion
    kdt_dict = {}

    # create a KDTree for each champion
    for championId in df["championId"].unique():
        champion_data = df[df["championId"] == championId].iloc[:, 31:]
        kdt_dict[championId] = KDTree(champion_data)

    return kdt_dict


def load_champ_df(champ_df_filepath="data/champ_df.csv"):
    # load in champ_df
    champ_df = pd.read_csv(champ_df_filepath)

    return champ_df


def champ_name_to_id(champ_df, champ_names):
    """returns champ ids list from champ names list"""
    champ_list = []
    for champ in champ_names:
        champId = champ_df[champ_df["name"] == champ]["key"].array[0]
        champ_list.append(champId)
    return champ_list


def convert_query(champ_list, champ_df, norm_dict):
    # champ_df indices we want
    cols = champ_df.columns[4:].to_list()
    # create unique for ally and enemy sums
    ally_cols = ["ally_" + x for x in cols]
    enemy_cols = ["enemy_" + x for x in cols]

    ally_ids = champ_list[0:5]
    enemy_ids = champ_list[5:10]
    ally_stats = champ_df[champ_df["key"].isin(ally_ids)].sum()[4:].to_list()
    enemy_stats = champ_df[champ_df["key"].isin(enemy_ids)].sum()[4:].to_list()

    stats = ally_stats + enemy_stats

    # new series to store vals in
    summed_features = pd.Series(data=stats, index=ally_cols + enemy_cols)

    # normalize features
    for key, value in norm_dict.items():
        summed_features[key] = (summed_features[key] - value[1]) / (value[0] - value[1])
    return summed_features


def query(df, champ_list, summed_features, kdt_dict):
    """
    takes in a champ list where 0 = self, 1-4 = allies, 5-9 = enemies
    """
    query = summed_features
    indices = kdt_dict[champ_list[0]].query(query, k=15, distance_upper_bound=2.0)
    # retrieve datapoints for desired champion
    result = df[df["championId"] == champ_list[0]].iloc[indices[1]]

    # filter out bad performances if pool is deep enough
    mask = (result["kda"] > 3) & (result["win"] == 1)
    if result[mask].shape[0] > 5:
        result = result[mask]

    return result


def load_item_data(version_filepath="data/version.json"):
    """Load in item data"""
    # open json file, get version
    f = open(version_filepath)
    version = json.load(f)[0]
    item_data_filepath = f"data/{version}/{version}/data/en_US/item.json"
    f = open(item_data_filepath, encoding="utf8")
    item_data = json.load(f)["data"]

    return item_data


def filter_items(item_recs, item_data):
    """Filter out items that are not valid for the build"""
    # filter item recs to only include boots and completed items
    item_recs_filtered = []  # nondestructive, new list
    boot_rec = False  # bool to store if a boot has been recommended
    for item in item_recs:
        item_valid = False  # bool to store if meets conditions
        item_desc = item_data[str(item)]  # get item info
        if (
            "Boots" in item_desc["tags"]
            and item_desc["gold"]["total"] > 350
            and item_desc["depth"] == 2
        ):  # if it is a boot and tier 2
            if not boot_rec:
                item_valid = True
                boot_rec = True
        if (
            item_desc["gold"]["total"] >= 2200
        ):  # if it costs more or equal to cheapest legendary item
            item_valid = True
        if (
            item_desc["gold"]["total"] > 1300
        ):  # filtering out starter items and components
            if (
                not item_desc["gold"]["purchasable"] == False
            ):  # if it is not purchasable, dont perform these checks
                if item_desc["depth"] == 3:  # if it is depth of 3, valid item
                    item_valid = True
                if item_desc["depth"] == 4:  # checking for ornn item, false if so
                    item_valid = False
        if item_valid:
            item_recs_filtered.append(item)

    return item_recs_filtered


def item_recommendations(result, item_data):
    item_matrix = result.iloc[:, 3:9].values.ravel()  # 1d np array of items
    item_matrix = item_matrix[item_matrix != 0]  # remove where no item

    items, count = np.unique(
        item_matrix, return_counts=True
    )  # get unique items and their counts
    count_sort = np.argsort(-count)  # sort by count descending
    item_recs = items[count_sort]  # sort items by count descending

    item_recs_filtered = filter_items(item_recs, item_data)

    return item_recs_filtered


def get_client_champ_data(install_path=None):
    """
    Get champ select data from local client
    Auto uses default install directory for each OS, can specify install_path to force
    """
    system = platform.system()

    if not install_path:
        if system == "Linux":
            user_id = os.getuid()
            user_info = pwd.getpwuid(user_id)
            username = user_info.pw_name
            install_path = f"/home/{username}/Games/league-of-legends/drive_c/Riot Games/League of Legends/"

        elif system == "Windows":
            install_path = "C:/Riot Games/League of Legends/"

        elif system == "Darwin":
            install_path = "/Applications/League of Legends.app/Contents/LoL/"

    f = open(install_path + "lockfile", "r")
    client_info = f.read().split(sep=":")
    f.close()

    port = client_info[2]
    pw = client_info[3]
    auth = (
        "riot",
        pw,
    )  # auth tuple for requests. riot static username, password changes on client restart

    url = "https://127.0.0.1:" + port
    champ_sel = "/lol-champ-select/v1/session"
    current_champ = "/lol-champ-select/v1/current-champion"
    data = requests.get((url + champ_sel), auth=auth, verify=False)
    self_champ = requests.get((url + current_champ), auth=auth, verify=False).json()

    # construct champ list
    allies = [
        x["championId"] for x in data.json()["myTeam"] if x["championId"] != self_champ
    ]
    enemies = [x["championId"] for x in data.json()["theirTeam"]]
    champ_list = [self_champ] + allies + enemies

    return champ_list


def main():
    parser = argparse.ArgumentParser(
        description="Get item recommendations for a given champion"
    )
    parser.add_argument(
        "-m",
        "--manual",
        dest="champ_names",
        type=str,
        nargs="+",
        required=False,
        help="Champion names as strings, 0 = self, 1-4 = allies, 5-9 = enemies",
    )
    parser.add_argument(
        "-c",
        "--client",
        dest="client",
        action="store_true",
        required=False,
        help="Get champion data from client",
    )
    args = parser.parse_args()

    if args.champ_names is None and args.client is False:
        print("No arguments given, please use -h for help")
        return

    # load in data
    print("Loading dataframe...")
    df = load_data(table="match_features")
    # normalize df
    print("Normalizing dataframe...")
    df_scaled, norm_dict = normalize_df(df)
    # create trees
    print("Creating trees...")
    kdt_dict = create_trees(df_scaled)
    # load in champion data
    print("Loading champion data...")
    champ_df = load_champ_df()
    # convert query
    print("Converting query...")

    if args.client:
        try:
            champ_list = get_client_champ_data()
        except:
            print("Client not running or no game in progress")
            raise
    else:
        champ_names = args.champ_names
        champ_list = champ_name_to_id(champ_df, champ_names)

    summed_features = convert_query(champ_list, champ_df, norm_dict)
    # query
    print("Querying...")
    result = query(df, champ_list, summed_features, kdt_dict)
    # load in item data
    print("Loading item data...")
    item_data = load_item_data()
    # get item recommendations
    print("Getting item recommendations...")
    print(
        f"\n\nRecommended items for your champ, in order of build frequency in similar games:"
    )
    item_recs = item_recommendations(result, item_data)

    print([item_data[str(x)]["name"] for x in item_recs])


if __name__ == "__main__":
    main()
