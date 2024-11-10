from cassiopeia import ChampionMastery, Match, Summoner


def get_summoner_by_name(name: str, region: str):
    summoner = Summoner(name=name, region=region)
    return summoner


def get_champion_masteries(summoner: Summoner):
    cm = ChampionMastery(summoner=summoner)
    return cm


def get_league_entries(summoner: Summoner):
    return summoner.league_entries()


def get_match(match_id: int, region: str):
    return Match(id=match_id, region=region)
