"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# NBA Schemas
class TennisBase(BaseModel):
    """Base NBA schema with common fields."""
    match_id: Optional[str] = None
    tournament: Optional[str] = None
    date: Optional[datetime] = None
    round: Optional[str] = None
    surface: Optional[str] = None
    player1_name: Optional[str] = None
    player1_rank: Optional[int] = None
    player1_country: Optional[str] = None
    player2_name: Optional[str] = None
    player2_rank: Optional[int] = None
    player2_country: Optional[str] = None
    winner: Optional[str] = None
    score: Optional[str] = None
    sets: Optional[str] = None
    duration_minutes: Optional[int] = None


class TennisCreate(TennisBase):
    """Schema for creating Tennis records."""
    match_id: str
    tournament: str
    date: datetime
    player1_name: str
    player2_name: str


class TennisResponse(TennisBase):
    """Schema for Tennis API responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TennisList(BaseModel):
    """Schema for paginated Tennis list responses."""
    items: List[TennisResponse]
    total: int
    page: int
    size: int
    pages: int


# Football Schemas
class FootballBase(BaseModel):
    """Base Football schema with common fields."""
    season: Optional[str] = None
    league: Optional[str] = None
    team: Optional[str] = None
    league_name: Optional[str] = None
    franchise: Optional[str] = None
    games_played: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    win_percentage: Optional[float] = None
    goals_scored: Optional[int] = None
    goals_conceded: Optional[int] = None
    point_differential: Optional[int] = None
    season_rank: Optional[int] = None
    sport: Optional[str] = None


class FootballCreate(FootballBase):
    """Schema for creating Football records."""
    season: str
    league: str
    team: str
    league_name: str
    sport: str


class FootballResponse(FootballBase):
    """Schema for Football API responses."""
    
    class Config:
        from_attributes = True


class FootballList(BaseModel):
    """Schema for paginated Football list responses."""
    items: List[FootballResponse]
    total: int
    page: int
    size: int
    pages: int


# Filter Schemas
class TennisFilters(BaseModel):
    """Filters for Tennis data queries."""
    tournament: Optional[str] = None
    surface: Optional[str] = None
    player: Optional[str] = None  # Searches both player1_name and player2_name
    country: Optional[str] = None
    year: Optional[int] = None
    winner: Optional[str] = None


class FootballFilters(BaseModel):
    """Filters for Football data queries."""
    league: Optional[str] = None
    season: Optional[str] = None
    team: Optional[str] = None
    league_name: Optional[str] = None
    franchise: Optional[str] = None
    sport: Optional[str] = None


# Pagination Schema
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")


# Statistics Schemas
class TennisStats(BaseModel):
    """Tennis statistics summary."""
    total_matches: int
    unique_players: int
    tournaments: List[str]
    surfaces: List[str]
    top_players: List[dict]


class FootballStats(BaseModel):
    """Football statistics summary."""
    total_teams: int
    leagues: List[str]
    seasons: List[str]
    sports: List[str]
    top_teams: List[dict]