"""
Database models for sports data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .database import Base


class Tennis(Base):
    """Tennis matches and player data model."""
    __tablename__ = "tennis"
    
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
    """Football matches and team data model."""
    __tablename__ = "football"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Match Information
    match_id = Column(String, unique=True, index=True)
    league = Column(String, index=True)
    season = Column(String, index=True)
    date = Column(DateTime, index=True)
    week = Column(Integer)
    stadium = Column(String)
    
    # Team Information
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    
    # Match Results
    home_score = Column(Integer)
    away_score = Column(Integer)
    winner = Column(String, index=True)  # 'home', 'away', 'draw'
    final_result = Column(String)  # Full score like "2-1"
    
    # Match Details
    attendance = Column(Integer)
    referee = Column(String)
    weather = Column(String)
    temperature = Column(Float)
    
    # Statistics (if available)
    home_possession = Column(Float)
    away_possession = Column(Float)
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())