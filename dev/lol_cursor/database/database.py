import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.schema import UniqueConstraint

DATABASE_URL = "postgresql+asyncpg://postgres:gl94hhp89k2YpcVx@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)


class Account(BaseModel):
    __tablename__ = "accounts"
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    riot_game_name = Column(String, index=True)
    riot_tag_line = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Summoner(BaseModel):
    __tablename__ = "summoners"
    summoner_name = Column(String, index=True)
    region = Column(String)
    profile_icon_id = Column(Integer)
    summoner_level = Column(Integer)
    puuid = Column(String, unique=True)
    summoner_id = Column(String, unique=True)
    account_id = Column(String, unique=True)
    UniqueConstraint("puuid", name="uix_1")


class ChampionMastery(BaseModel):
    __tablename__ = "champion_masteries"
    puuid = Column(String, ForeignKey("summoners.puuid"))
    champion_id = Column(Integer)
    mastery_level = Column(Integer)
    mastery_points = Column(Integer)


class LeagueInfo(BaseModel):
    __tablename__ = "league_info"
    summoner_id = Column(String, ForeignKey("summoners.summoner_id"))
    queue_type = Column(String)
    rank = Column(String)
    tier = Column(String)
    league_points = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)


class MatchData(BaseModel):
    __tablename__ = "match_data"
    puuid = Column(String)
    match_id = Column(String)
    game_creation = Column(BigInteger)
    game_duration = Column(Integer)
    queue_id = Column(Integer)
    champion_id = Column(Integer)
    champion_name = Column(String)
    team_id = Column(Integer)
    win = Column(Boolean)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    total_damage_dealt_to_champions = Column(Integer)
    total_damage_taken = Column(Integer)
    vision_score = Column(Integer)
    gold_earned = Column(Integer)
    total_minions_killed = Column(Integer)


@asynccontextmanager
async def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
