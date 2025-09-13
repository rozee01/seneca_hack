from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .database import Base


class Nba(Base):
    """NBA team statistics model."""
    __tablename__ = "nba_stats"
    
    # Composite primary key matching your exact table structure
    season = Column(String, primary_key=True, index=True)
    league = Column(String, primary_key=True, index=True)
    team_id = Column(String, primary_key=True, index=True)
    
    # Columns exactly as in your table: season | league | league_name | team_id | franchise | games_played | wins | losses | draws | win_percentage | goals_scored | goals_conceded | point_differential | sport | season_rank
    league_name = Column(String, index=True)
    franchise = Column(String)
    games_played = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    draws = Column(Integer)
    win_percentage = Column(Float)
    goals_scored = Column(Integer)  # total_points_scored in NBA context
    goals_conceded = Column(Integer)  # total_points_conceded in NBA context
    point_differential = Column(Float)
    sport = Column(String, index=True)
    season_rank = Column(Integer)


class Football(Base):
    """Football team season statistics model."""
    __tablename__ = "football_stats"
    
    # Composite primary key matching your exact table structure
    season = Column(String, primary_key=True, index=True)
    league = Column(String, primary_key=True, index=True)
    team = Column(String, primary_key=True, index=True)
    
    # Columns exactly as in your table: season | league | league_name | team | franchise | games_played | wins | losses | draws | win_percentage | goals_scored | goals_conceded | point_differential | season_rank | sport
    league_name = Column(String, index=True)
    franchise = Column(String)
    games_played = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    draws = Column(Integer)
    win_percentage = Column(Float)
    goals_scored = Column(Integer)
    goals_conceded = Column(Integer)
    point_differential = Column(Integer)
    season_rank = Column(Integer)
    sport = Column(String, index=True)