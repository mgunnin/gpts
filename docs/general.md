# League of Legends Data Analysis and Visualization

The application is designed to interact with the Riot Games API to fetch and process data related to the game League of Legends. It utilizes FastAPI for creating a web server that exposes several endpoints to retrieve data about summoners, their champion mastery, league information, and match details. The application is structured into several key components, each responsible for a specific aspect of the application's functionality:

## Main Components

1. FastAPI Web Server (main.py)

- Serves as the entry point of the application, defining various API endpoints that allow users to query for League of Legends data.
- Utilizes CORS middleware to handle cross-origin requests.
- Defines endpoints for fetching summoner information, champion mastery, total champion mastery score, summoner leagues, match lists, match details, and calculating player performance.
- Includes a background task to populate the database with top players' information upon startup.
- Serves static files like the application logo and plugin manifest.

2. Database Interface (database_pg.py)

- Provides a wrapper around PostgreSQL database operations, facilitating connection management, query execution, and table creation.
- Defines methods for executing raw SQL queries, inserting performance data, and processing predictor data.
- Contains the ProcessPerformance class for calculating player performance metrics based on match details.

3. Riot API Wrapper (riot_api.py)

- Encapsulates the logic for interacting with the Riot Games API, including fetching summoner information, champion mastery, match IDs, match timelines, and detailed match information.
- Provides methods for determining the overall region based on the summoner's region, extracting matches, and downloading match details.
- Includes functionality to populate the database with top players' information across different regions and queues.

4. Data Extraction Script (extract_pg.py)

- A standalone script that can be run to perform various data mining operations such as populating the database with player lists, match lists, and downloading match details.
- Utilizes the RiotAPI class to fetch data from the Riot Games API and the Database class to store the fetched data.

## Key Features

- Summoner Data Retrieval: Fetches summoner information including PUUID (Player Universally Unique Identifier) based on summoner name and region.
- Champion Mastery Information: Retrieves a summoner's mastery information for all champions, including mastery level, total mastery points, and other related data.
- League Information: Fetches league information for a given summoner, including rank, LP (League Points), win rate, and promotion status.
- Match Data Processing: Downloads and processes match details and timelines, extracting relevant data for further analysis.
- Player Performance Calculation: Calculates performance metrics for players based on match details, such as deaths per minute, kills and assists per minute, and total damage dealt per minute.
- Database Management: Manages a PostgreSQL database to store and retrieve League of Legends data, including player information, match details, and performance metrics.
- Background Data Population: Automatically populates the database with top players' information from different regions and queues upon application startup.

## Potential Improvements

- Real-Time Data Updates: Implement a scheduling mechanism to periodically update the database with the latest data from the Riot Games API, ensuring that the information remains current.
- Advanced Analytics: Introduce more sophisticated analytics and machine learning models to predict match outcomes, player performance, and champion recommendations based on historical data.
- User Authentication: Add user authentication to allow users to securely access their data and preferences, enabling personalized insights and recommendations.
- Interactive Dashboard: Develop an interactive web dashboard that provides users with visualizations of their performance metrics, match histories, and comparative analytics against top players.
- API Rate Limiting: Implement rate limiting on the FastAPI server to manage the load and prevent abuse of the API endpoints.
