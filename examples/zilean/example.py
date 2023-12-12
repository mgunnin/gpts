from zilean import TimelineCrawler, SnapShots, read_api_key
import pandas as pd

# Use the TimelineCrawler to fetch `MatchTimelineDto`s
# from Riot. The `MatchTimelineDto`s have game stats
# at each minute mark.

# We need a API key to fetch data. See the Riot Developer
# Portal for more info.
api_key = read_api_key("RGAPI-de85bb37-76e5-6890-9a94-fcf7b1bf14a6")
# Crawl 2000 Diamond RANKED_SOLO_5x5 timelines from the Korean server.
crawler = TimelineCrawler(api_key, region="na1",
                          tier="DIAMOND", queue="RANKED_SOLO_5x5")
result = crawler.crawl(50, match_per_id=30, file="results.json")
# This will take a long time!

# We will look at the player statistics at 10 and 15 minute mark.
snaps = SnapShots(result, frames=[10, 15])

# Store the player statistics using in a pandas DataFrame
player_stats = snaps.summary(per_frame=True)
data = pd.DataFrame(player_stats)

# Look at the distribution of totalGold difference for `player 0` (TOP player)
# at 15 minutes mark.
sns.displot(x="totalGold_0", data=data[data['frame'] == 15], hue="win")