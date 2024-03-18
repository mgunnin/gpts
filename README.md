# League of Legends Optimizer

- [Overview](https://oracle-devrel.github.io/leagueoflegends-optimizer/)
- [Model Building with scikit-learn and AutoGluon](https://oracle-devrel.github.io/leagueoflegends-optimizer/hols/workshops/mlwithoci/index.html) - Illustrates the whole AI process once we have data available
- [League of Legends Machine Learning with OCI - Data Extraction](https://oracle-devrel.github.io/leagueoflegends-optimizer/hols/workshops/dataextraction/index.html)

## Player Data Acquisition

1. Create local sqlite3 database
   `python src/init_db.py`

2. Extract player data
   `python src/sqlite_league.py`

3. Extract previously played matches' ID from pool of players in the database
   `python src/sqlite_league.py --mode="match_list"`

4. Process each player's performance
   `python src/process_performance.py`

5. Generate 3 csv files from database
   `python src/read_data.py`
   - performance_report.csv, with the processed data ready for ML
   - player_report.csv, with various player information (Masters+)
   - match_report.csv, with every player's extracted matches.

## League.py

`python league.py --mode="player_list"`

`python league.py --mode="match_list"`

- Then, once we have the data, we process this data using the process_predictor_liveclient option

`python league.py --mode="process_predictor_liveclient"`

## Documentation for League of Legends Data Mining and Analysis App

This document provides detailed information about the Python codebase for the League of Legends data mining and analysis application.

### Overview

The application interacts with the Riot Games API to collect match data and player information, storing it in a Supabase database. It provides functionality for:

- Data Mining:
  - Fetching top players from various regions and queues.
  - Collecting match lists for players.
  - Downloading detailed match information.
- Data Processing:
  - Calculating player performance metrics.
  - Inserting processed data into the database.
- API Endpoints:
- Retrieving summoner information.
- Getting champion mastery details.
- Accessing match lists and detailed match data.
- Calculating player performance for specific matches.

## Code Structure

The codebase is organized into several Python files:

- database_pg.py: Contains the Database class, which handles database connections and operations, and the ProcessPerformance class, which calculates player performance metrics.
- riot_api.py: Contains the RiotAPI class, which interacts with the Riot Games API to fetch data.
- main.py: Contains the main execution logic and handles user input for selecting the data mining mode.
- app.py: Contains the FastAPI application that provides API endpoints for accessing and processing the collected data.
- extract_data.py: Contains the functions for extracting data from the Riot API and pushing it to Supabase

### Detailed Function and Method Descriptions

- database_pg.py

  - Class: Database

    - **init**(self, database_path): Initializes the Database object with the database connection information.
    - execute_raw(self, sql, params=None): Executes raw SQL queries with optional parameters.
    - execute(self, query, params=None): Executes a query with optional parameters and returns a cursor object.
    - get_connection(self): Establishes a connection to the Supabase database.
    - get_sqlalchemy_engine(self): Creates a SQLAlchemy engine for interacting with the database.
    - run_init_db(self): Creates the necessary database tables if they don't exist.
    - change_column_value_by_key(self, table_name, column_name, column_value, key): Updates the value of a specific column in a table based on a given key.
    - process_predictor(self): Processes match details and inserts data into the predictor table
    - process_predictor_liveclient(self): Processes match details for the live client and inserts data into the predictor_liveclient table.

  - Class: ProcessPerformance

    - **init**(self, db): Initializes the ProcessPerformance object with the database connection information.
    - calculate_player_performance(self, participant_data, duration_m): Calculates player performance metrics based on participant data and match duration.
    - insert_performance_data(self, final_object): Inserts calculated performance data into the performance_table.
    - process_player_performance(self, obj, conn): Processes player performance data from a match and inserts it into the database.

  - Non-Class Functions:
    - extract_frame_data(frame, participant_id): Extracts relevant data from a frame in the match timeline for a specific participant.
    - build_final_object(json_object): Builds a list of dictionaries containing extracted data from a match JSON object.
    - build_final_object_liveclient(json_object): Builds a list of dictionaries for the live client data, using the extract_frame_data helper function.
    - extract_frame_data(frame, participant_id): Extracts relevant data from a frame in the match timeline for a specific participant.

- riot_api.py

  - Class: RiotAPI

    - **init**(self, db): Initializes the RiotAPI object with the database connection information and sets up headers for API requests.
    - get_puuid(self, request_ref, summoner_name, region, db): Retrieves the PUUID (Player Universally Unique Identifier) for a summoner.
    - get_summoner_information(self, summoner_name, request_region): Fetches summoner information based on the summoner name and region.
    - get_champion_mastery(self, puuid, request_region): Retrieves champion mastery information for a given player.
    - get_total_champion_mastery_score(self, puuid, request_region): Gets the total champion mastery score for a player.
    - get_summoner_leagues(self, summonerId, region): Retrieves league information for a summoner.
    - get_match_ids(self, puuid, num_matches, queue_type, region): Fetches a list of match IDs for a player.
    - get_match_timeline(self, match_id, region): Retrieves the timeline data for a match.
    - get_match_info(self, match_id, region): Fetches detailed match information.
    - determine_overall_region(self, region): Determines the overall region (e.g., "europe", "americas", "asia") based on the specific region code.
    - get_top_players(self, region, queue, db): Retrieves top players from a region and queue and inserts them into the database.
    - extract_matches(self, region, match_id, db, key): Extracts 1v1 matchup data from a match and inserts it into the database.
    - player_list(self): Triggers the process of fetching top players from all regions and queues.
    - match_list(self): Collects match lists for players in the database.
    - match_download_standard(self, db): Downloads standard match information for unprocessed matches.
    - match_download_detail(self, db): Downloads detailed match information for unprocessed matches.

- main.py
  - data_mine(db, mode): Controls the data mining process based on the selected mode (e.g., "player_list", "match_list").
  - main(mode): Initializes the database and starts the data mining process.
- app.py
  - populate_database(): Background task that populates the database with top players' information.
  - lifespan(): Lifespan event handler that triggers the populate_database task.

### API Endpoints

- /summoner/{summoner_name}: Retrieves summoner information.
- /champion_mastery/{puuid}: Gets champion mastery details.
- /champion_mastery/scores/{puuid}: Retrieves total champion mastery score.
- /summoner/leagues/{summonerId}: Gets league information for a summoner.
- /match_list/{puuid}: Fetches a list of match IDs.
- /match_detail/{match_id}: Retrieves detailed match information.
- /performance: Calculates player performance for a match.
- /: Home endpoint.
- /public/logo.png: Serves the plugin logo image.
- /.well-known/ai-plugin.json: Provides the AI plugin manifest.
- /openapi.yaml: Serves the OpenAPI specification.

### Additional Notes

- The code uses environment variables to store sensitive information like API keys and database credentials.
- The app.py file uses FastAPI to create a web API for accessing and processing the data.
- The code includes error handling and logging to help diagnose issues.
- This documentation provides a comprehensive overview of the codebase. For more specific details, refer to the comments and docstrings within the individual functions and methods.

## Potential Improvements

- Real-Time Data Updates: Implement a scheduling mechanism to periodically update the database with the latest data from the Riot Games API, ensuring that the information remains current.
- Advanced Analytics: Introduce more sophisticated analytics and machine learning models to predict match outcomes, player performance, and champion recommendations based on historical data.
- User Authentication: Add user authentication to allow users to securely access their data and preferences, enabling personalized insights and recommendations.
- Interactive Dashboard: Develop an interactive web dashboard that provides users with visualizations of their performance metrics, match histories, and comparative analytics against top players.
- API Rate Limiting: Implement rate limiting on the FastAPI server to manage the load and prevent abuse of the API endpoints.
