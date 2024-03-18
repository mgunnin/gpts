# AI Application Development Prompt

## GPT/Cursor

We are embarking on the development of a sophisticated application designed to leverage the Riot Games API for in-depth data analysis and visualization related to League of Legends. The core of this application will be built around a FastAPI web server, which will serve as the backbone for handling requests and delivering data. This server will need to implement CORS middleware to support cross-origin requests effectively.

The application will interact with a PostgreSQL database, requiring a robust interface for seamless connection management, query execution, and dynamic table creation. This database will store a wide array of data, including summoner profiles, champion mastery details, league information, and comprehensive match analytics.

A critical component of our application will be the Riot API Wrapper, designed to encapsulate all interactions with the Riot Games API. This wrapper will fetch various data points such as summoner information, champion mastery, match IDs, and detailed match timelines. It will also be responsible for populating our database with top player information across different regions and queues, ensuring our data remains rich and relevant.

To facilitate data extraction and mining, we will develop a standalone script capable of running various operations to populate our database with player lists, match lists, and detailed match analyses. This script will leverage both the RiotAPI class for data fetching and the Database class for data storage.

Our application will offer several key features, including:

- Summoner Data Retrieval: Fetching detailed summoner profiles based on name and region.
- Champion Mastery Information: Providing comprehensive mastery stats for all champions for a given summoner.
- League Information: Offering insights into a summoner's league standings, including rank, LP, win rate, and promotion status.
- Match Data Processing: Analyzing match details and timelines to extract and present meaningful data.
- Player Performance Calculation: Computing performance metrics for players based on detailed match data.
- Database Management: Efficiently managing a PostgreSQL database to store and retrieve all collected data.
- Background Data Population: Automatically updating the database with top player information from various regions upon application startup.

To enhance the capabilities of our application, we propose the following improvements and additional features:

- Real-Time Data Updates: Implementing a scheduling mechanism to periodically refresh our database with the latest data from the Riot Games API.
- Advanced Analytics: Introducing sophisticated analytics and machine learning models to predict match outcomes, player performance, and offer champion recommendations based on historical data.
- User Authentication: Adding a secure authentication layer to enable users to access their data and preferences, providing a personalized experience.
- Interactive Dashboard: Developing a dynamic web dashboard that offers users visualizations of their performance metrics, match histories, and allows for comparisons against top players.
- API Rate Limiting: Establishing rate limiting on our FastAPI server to manage load and prevent API abuse.

This application aims to be a comprehensive tool for League of Legends players and enthusiasts, offering deep insights and analytics to help improve their gameplay and understanding of the game.

## Google Gemini

### League of Legends Data Analysis and Prediction App

We are developing an application that leverages AI to analyze League of Legends match data and provide insights and predictions to players. The application should:

1. Data Collection and Management:
   - Interact with the Riot Games API to collect match data, including timelines and detailed participant statistics.
   - Store the collected data efficiently in a Supabase database, handling potential duplicates and ensuring data integrity.
   - Implement robust error handling and logging mechanisms to track API requests and database operations.
2. Data Analysis and Feature Engineering:
   - Calculate various player performance metrics, such as kills per minute, deaths per minute, gold per minute, and a composite performance score.
   - Extract meaningful features from the match data, including champion picks, team compositions, objective control, and individual player contributions.
   - Employ dimensionality reduction techniques if necessary to handle high-dimensional data.
3. Predictive Modeling:
   - Train machine learning models on the processed data to predict match outcomes and individual player performance.
   - Experiment with different model architectures, such as decision trees, support vector machines, or neural networks, to find the best performing model.
   - Evaluate model performance using appropriate metrics like accuracy, precision, recall, and F1-score.
4. User Interface and Visualization:
   - Develop a user-friendly interface that allows players to:
   - Search for summoners and view their match history.
   - Analyze individual match details and player performance metrics.
   - Get predictions for upcoming matches based on team compositions and player statistics.
   - Create visualizations to display match statistics, player performance trends, and model predictions in an intuitive and engaging way.

#### Additional Features and Improvements

1. Live Match Tracking:
   Integrate functionality to track live matches and update the database and predictions in real-time.
2. Personalized Recommendations:
   Provide personalized recommendations to players based on their playstyle, champion pool, and past performance.
3. Team Analysis:
   Offer insights into team synergy, strengths, and weaknesses based on match data and player statistics.
4. Advanced Statistics:
   Calculate and display advanced statistics, such as damage dealt/taken per minute, crowd control duration, and objective bounties.
5. Integration with Other Platforms:
   Explore integration with streaming platforms or social media to share insights and predictions with a wider audience.

#### AI Programming and Engineering Agent's Role

We expect the AI Programming and Engineering Agent to:

- Generate Python code for the application, including data collection, processing, modeling, and user interface components.
- Optimize the code for performance and efficiency, considering factors like rate limiting, parallel processing, and database optimization.
- Suggest and implement appropriate machine learning models and feature engineering techniques.
- Assist in designing and developing the user interface and visualizations.
- We believe that this application, with the help of the AI Programming and Engineering Agent, can provide valuable insights and predictions to League of Legends players, helping them improve their gameplay and decision-making.
