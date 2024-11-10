from typing import Any, Dict

from sqlalchemy.future import select

from database.database import MatchData, Summoner, get_db


class PlayerPerformance:
    def __init__(self):
        pass

    async def calculate_performance_metrics(
        self, summoner_name: str, region: str
    ) -> Dict[str, Any]:
        async with get_db() as db:
            summoner_info = await self._fetch_summoner_info(db, summoner_name, region)
            if not summoner_info:
                return {"error": "Summoner not found"}

            match_data_results = await self._fetch_match_data(db, summoner_info)
            if not match_data_results:
                return {"error": "No match data found for the summoner"}

            performance_metrics = self._calculate_metrics(match_data_results)

            return performance_metrics

    async def _fetch_summoner_info(self, db, summoner_name, region):
        result = await db.execute(
            select(Summoner).where(
                Summoner.summoner_name == summoner_name, Summoner.region == region
            )
        )
        summoner_info = result.scalars().first()
        return summoner_info

    async def _fetch_match_data(self, db, summoner_info):
        match_data_results = await db.execute(
            select(MatchData)
            .join(Summoner, Summoner.id == MatchData.summoner_id)
            .where(Summoner.id == summoner_info.id)
        )
        match_data_results = match_data_results.scalars().all()
        return match_data_results

    def _calculate_metrics(self, match_data_results):
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        for match in match_data_results:
            total_kills += match.kills
            total_deaths += match.deaths
            total_assists += match.assists

        total_games = len(match_data_results)
        avg_kills = total_kills / total_games
        avg_deaths = total_deaths / total_games
        avg_assists = total_assists / total_games

        performance_metrics = {
            "average_kills": avg_kills,
            "average_deaths": avg_deaths,
            "average_assists": avg_assists,
            "total_games": total_games,
        }

        return performance_metrics


if __name__ == "__main__":
    import asyncio

    player_performance = PlayerPerformance()
    asyncio.run(
        player_performance.calculate_performance_metrics("SummonerName", "Region")
    )
