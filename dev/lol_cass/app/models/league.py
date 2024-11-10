from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    summoner_id = Column(String, ForeignKey("summoners.summoner_id"), index=True)
    summoner_name = Column(String)
    queue = Column(String)
    tier = Column(String)
    league_points = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    hot_streak = Column(Boolean)
    veteran = Column(Boolean)
    fresh_blood = Column(Boolean)
    inactive = Column(Boolean)
    games_played = Column(Integer)
    win_rate = Column(Float)
    promotion_series_progress = Column(String)
    highest_achieved_tier = Column(String)
    highest_achieved_rank = Column(String)
    highest_league_points = Column(Integer)

    summoner = relationship("Summoner", back_populates="leagues")
