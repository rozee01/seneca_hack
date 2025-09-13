"""
Database models for sports data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .database import Base


class Tennis(Base):
    """Tennis matches and player data model."""
    __tablename__ = "nba_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Match Information
    match_id = Column(String, unique=True, index=True)
    tournament = Column(String, index=True)
    date = Column(DateTime, index=True)
    round = Column(String)
    surface = Column(String, index=True)  # Hard, Clay, Grass, etc.
    
    # Player Information
    player1_name = Column(String, index=True)
    player1_rank = Column(Integer)
    player1_country = Column(String)
    player2_name = Column(String, index=True)
    player2_rank = Column(Integer)
    player2_country = Column(String)
    
    # Match Results
    winner = Column(String, index=True)
    score = Column(String)
    sets = Column(String)
    duration_minutes = Column(Integer)
    
    # Statistics (if available)
    player1_aces = Column(Integer)
    player1_double_faults = Column(Integer)
    player1_first_serve_percentage = Column(Float)
    player1_winners = Column(Integer)
    player1_unforced_errors = Column(Integer)
    
    player2_aces = Column(Integer)
    player2_double_faults = Column(Integer)
    player2_first_serve_percentage = Column(Float)
    player2_winners = Column(Integer)
    player2_unforced_errors = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Football(Base):
    """Football team season statistics model."""
    __tablename__ = "football_stats"
    
    # Using season + league + team as composite key since there's no id column
    season = Column(String, primary_key=True, index=True)
    league = Column(String, primary_key=True, index=True)
    team = Column(String, primary_key=True, index=True)
    
    # League and Team Information
    league_name = Column(String, index=True)
    franchise = Column(String)
    
    # Season Statistics
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