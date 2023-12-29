from database import Database
from lol_api import LolAPI
from chatgpt import ChatGPT
import json

with open('config.json') as config_file:
    config = json.load(config_file)

def main():
    # Initialize the Database
    db_config = config['DATABASE']
    db = Database(db_config['HOST'], db_config['PORT'], db_config['USER'], db_config['PASSWORD'], db_config['DB_NAME'])

    # Initialize the League of Legends API
    lol_api = LolAPI(config['LOL_API_KEY'])

    # Initialize the ChatGPT
    chatgpt = ChatGPT(config['CHATGPT']['MODEL_NAME'], config['CHATGPT']['TOKEN'])

    # Initialize the Analysis
    analysis = Analysis()

    # Main loop
    while True:
        # Request user summoner name
        summoner_name = input("Enter the name of the League of Legends player: ")

        # Retrieve player's match statistics
        player_stats = lol_api.get_player_stats(summoner_name)

        # Check if player_stats is None
        if player_stats is None:
            print("No stats found for this player.")
            continue

        # Save player's match statistics to the database
        db.save_player_stats(summoner_name, player_stats)

        # Analyze player's match statistics
        analysis_result = analysis.analyze(player_stats)

        # Check if analysis_result is None
        if analysis_result is None:
            print("No analysis result found for this player.")
            continue

        # Generate coaching advice
        advice = chatgpt.generate_advice(analysis_result)

        # Print the advice
        print(advice)

class Analysis:
    def __init__(self):
        pass

    def analyze(self, player_stats):
        # Initialize the analysis result
        pass


if __name__ == "__main__":
    main()
