from cassiopeia import cassiopeia as cass
from cassiopeia.core import Match, MatchHistory, Summoner
from dotenv import load_dotenv
from fastapi import APIRouter

load_dotenv()
cass.set_riot_api_key("RIOT_API_KEY")

cass_router = APIRouter()

cass.get_summoner(name="gameb0x", region="NA")

@cass_router.get("/participants_data/{participants}")
async def get_participant_data(participants):
    team_participant_data = []
    for p in participants:
        p_data = {"summoner": p.summoner.name, "champion": p.champion.name, "runes": p.runes.keystone.name,
                  "d_spell": p.summoner_spell_d.name, "f_spell": p.summoner_spell_f.name,
                  "kills": p.stats.kills, "assist": p.stats.assists, "deaths": p.stats.deaths,
                  "kda_ratio": round(p.stats.kda, 2), "damage_dealt": p.stats.total_damage_dealt,
                  "creep_score": p.stats.total_minions_killed, "vision_score": p.stats.vision_score}

        p_items = []
        number_of_item_slots = 6
        for i in range(number_of_item_slots):
            try:
                p_items.append(p.stats.items[i].name)
            except AttributeError:
                p_items.append("None")
        p_data["items"] = p_items
        team_participant_data.append(p_data)
    return team_participant_data

def get_team_data(team):
    team_data = {"team_id": team.id,
                 "win": team.win,
                 "first_blood": team.first_blood,
                 "first_tower": team.first_tower,
                 "first_inhibitor": team.first_inhibitor,
                 "first_baron": team.first_baron,
                 "first_dragon": team.first_dragon,
                 "first_rift_herald": team.first_rift_herald, "tower_kills": team.tower_kills,
                 "inhibitor_kills": team.inhibitor_kills,
                 "baron_kills": team.baron_kills,
                 "dragon_kills": team.dragon_kills,
                 "rift_herald_kills": team.rift_herald_kills,
                 "bans": team.bans}
    return team_data


if __name__ == "__main__":
    main()
