from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Summoner(Base):
    __tablename__ = "summoners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(String, unique=True, index=True)
    summoner_id = Column(String, unique=True, index=True)
    puuid = Column(String, unique=True, index=True)
    summoner_name = Column(String)
    profile_icon_id = Column(Integer)
    summoner_level = Column(Integer)
    region = Column(String)
    last_updated = Column(DateTime, onupdate=datetime.now)

    champion_masteries = relationship("ChampionMastery", back_populates="summoner")
    leagues = relationship("League", back_populates="summoner")
    match_participants = relationship("MatchParticipant", back_populates="summoner")
