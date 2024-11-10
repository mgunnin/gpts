from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, index=True)
    region = Column(String)
    platform_id = Column(String)
    game_id = Column(Integer)
    queue_id = Column(Integer)
    season_id = Column(Integer)
    game_version = Column(String)
    game_mode = Column(String)
    map_id = Column(Integer)
    game_type = Column(String)
    start_time = Column(DateTime)
    duration = Column(Integer)

    participants = relationship("MatchParticipant", back_populates="match")
