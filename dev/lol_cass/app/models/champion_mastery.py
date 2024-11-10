from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChampionMastery(Base):
    __tablename__ = "champion_masteries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    summoner_id = Column(String, ForeignKey("summoners.summoner_id"), index=True)
    champion_id = Column(Integer)
    champion_level = Column(Integer)
    champion_points = Column(Integer)
    last_play_time = Column(Integer)
    champion_points_until_next_level = Column(Integer)
    chest_granted = Column(Integer)
    tokens_earned = Column(Integer)
    points_since_last_level = Column(Integer)
    games_played = Column(Integer)

    summoner = relationship("Summoner", back_populates="champion_masteries")
