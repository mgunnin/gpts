from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class MatchParticipant(Base):
    __tablename__ = "match_participants"

    id = Column(Integer, primary_key=True, index=True)
    summoner_id = Column(String, ForeignKey("summoners.summoner_id"))
    match_id = Column(String, ForeignKey("matches.match_id"))
    champion_id = Column(Integer)
    team_id = Column(String)
    lane = Column(String)
    role = Column(String)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    gold_earned = Column(Integer)
    damage_dealt = Column(Integer)
    damage_taken = Column(Integer)
    wards_placed = Column(Integer)
    wards_killed = Column(Integer)
    vision_wards_bought = Column(Integer)
    cs = Column(Integer)
    vision_score = Column(Integer)
    first_blood = Column(Boolean)
    first_tower = Column(Boolean)
    first_inhibitor = Column(Boolean)
    first_baron = Column(Boolean)
    first_dragon = Column(Boolean)
    first_rift_herald = Column(Boolean)
    tower_kills = Column(Integer)
    inhibitor_kills = Column(Integer)
    baron_kills = Column(Integer)
    dragon_kills = Column(Integer)
    rift_herald_kills = Column(Integer)
    items = Column(String)
    spells = Column(String)
    runes = Column(String)
    summoner_spells = Column(String)
    win = Column(Boolean)

    match = relationship("Match", back_populates="participants")
    summoner = relationship("Summoner", back_populates="match_participants")
