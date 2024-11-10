import asyncio

from cassiopeia import Queue, Summoner

from app.api.riot import (get_champion_masteries, get_league_entries,
                          get_match, get_summoner_by_name)
from app.db.database import AsyncSessionLocal
from app.models.champion_mastery import ChampionMastery
from app.models.league import League
from app.models.match import Match
from app.models.match_participant import MatchParticipant
from app.models.summoner import Summoner as SummonerModel


async def populate_data():
    db = await AsyncSessionLocal()

    regions = ["NA1", "EUW1", "KR"]
    queues = [Queue.ranked_solo_fives, Queue.ranked_flex_fives]

    await asyncio.gather(
        *[
            process_region_queue(db, region, queue)
            for region in regions
            for queue in queues
        ]
    )

    await db.commit()
    await db.close()


async def process_player(db, player, region):
    summoner = await get_summoner_by_name(player.summoner_name, region)
    db_summoner = SummonerModel(
        summoner_id=summoner.id,
        account_id=summoner.account_id,
        puuid=summoner.puuid,
        summoner_name=summoner.name,
        profile_icon_id=summoner.profile_icon,
        summoner_level=summoner.level,
        region=region,
    )
    await db.merge(db_summoner)

    await populate_champion_masteries(db, summoner, db_summoner)
    await populate_league_entries(db, summoner, db_summoner)
    await populate_matches(db, summoner, region)


async def process_region_queue(db, region, queue):
    top_players = await get_top_players(region, queue)
    await asyncio.gather(
        *[process_player(db, player, region) for player in top_players]
    )


async def get_top_players(region, queue):
    # Fetch the list of top players for the specified region and queue
    top_players = await Summoner.paginate(
        region=region, queue=queue, page=1, per_page=10
    )
    return top_players


async def populate_champion_masteries(db, summoner, db_summoner):
    masteries = await get_champion_masteries(summoner)
    db_masteries = []
    for mastery in masteries:
        db_mastery = ChampionMastery(
            summoner_id=db_summoner.id,
            champion_id=mastery.champion_id,
            champion_level=mastery.champion_level,
            champion_points=mastery.champion_points,
            last_play_time=mastery.last_play_time,
            champion_points_until_next_level=mastery.champion_points_until_next_level,
            chest_granted=mastery.chest_granted,
            tokens_earned=mastery.tokens_earned,
        )
        db_masteries.append(db_mastery)
    db.bulk_save_objects(db_masteries)


async def populate_league_entries(db, summoner, db_summoner):
    league_entries = await get_league_entries(summoner)
    db_league_entries = []
    for entry in league_entries:
        db_entry = League(
            summoner_id=db_summoner.id,
            queue=entry.queue,
            tier=entry.tier,
            rank=entry.rank,
            league_points=entry.league_points,
            wins=entry.wins,
            losses=entry.losses,
            hot_streak=entry.hot_streak,
            veteran=entry.veteran,
            fresh_blood=entry.fresh_blood,
            inactive=entry.inactive,
        )
        db_league_entries.append(db_entry)
    db.bulk_save_objects(db_league_entries)


async def populate_matches(db, summoner, region):
    match_history = await summoner.match_history
    for match_reference in match_history:
        match_id = match_reference.id
        match = await get_match(match_id, region)

        db_match = Match(
            match_id=match.id,
            region=region,
            platform_id=match.platform.value,
            game_id=match.game_id,
            queue_id=match.queue_id,
            season_id=match.season_id,
            timestamp=match.creation.timestamp(),
        )
        db.merge(db_match)

        db_participants = []
        for participant in match.participants:
            db_participant = MatchParticipant(
                match_id=match.id,
                summoner_id=participant.summoner.id,
                champion_id=participant.champion.id,
                team_id=participant.team.side.value,
                lane=participant.lane.value,
                role=participant.role.value,
                kills=participant.stats.kills,
                deaths=participant.stats.deaths,
                assists=participant.stats.assists,
                gold_earned=participant.stats.gold_earned,
                damage_dealt=participant.stats.total_damage_dealt_to_champions,
                damage_taken=participant.stats.total_damage_taken,
                wards_placed=participant.stats.wards_placed,
                wards_killed=participant.stats.wards_killed,
                vision_wards_bought=participant.stats.vision_wards_bought,
                cs=participant.stats.total_minions_killed,
                win=participant.stats.win,
            )
            db_participants.append(db_participant)

        db.bulk_save_objects(db_participants)
