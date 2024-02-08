# League of Legends Optimizer

- [Overview](https://oracle-devrel.github.io/leagueoflegends-optimizer/)
- [Model Building with scikit-learn and AutoGluon](https://oracle-devrel.github.io/leagueoflegends-optimizer/hols/workshops/mlwithoci/index.html) - Illustrates the whole AI process once we have data available
- [League of Legends Machine Learning with OCI - Data Extraction](https://oracle-devrel.github.io/leagueoflegends-optimizer/hols/workshops/dataextraction/index.html)

## Player Data Acquisition

1. Create local sqlite3 database
   `python src/init_db.py`

2. Extract player data
   `python src/cloudshell_league.py`

3. Extract previously played matches' ID from pool of players in the database
   `python src/cloudshell_league.py --mode="match_list"`

4. Process each player's performance
   `python src/cloudshell_process_performance.py`

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
