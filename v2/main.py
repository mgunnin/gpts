from database import Database
from riot_api import RiotAPI


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
    elif mode == "process_predictor":
        db.process_predictor()
    elif mode == "process_predictor_liveclient":
        db.process_predictor_liveclient()
    else:
        api.player_list()
        api.match_list()
        api.match_download_standard(db)
        api.match_download_detail(db)

def main(mode):
    db = Database("lol_gpt_v3.db")
    db.run_init_db()
    data_mine(db, mode)


if __name__ == "__main__":
    mode = input("Enter mode (player_list/match_list): ")
    main(mode)
