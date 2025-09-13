"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# Tennis Schemas
class TennisBase(BaseModel):
    """Base Tennis schema with common fields."""
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
    match_id: Optional[str] = None
    league: Optional[str] = None
    season: Optional[str] = None
    date: Optional[datetime] = None
    week: Optional[int] = None
    stadium: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[str] = None
    final_result: Optional[str] = None
    attendance: Optional[int] = None
    referee: Optional[str] = None


class FootballCreate(FootballBase):
    """Schema for creating Football records."""
    match_id: str
    league: str
    season: str
    date: datetime
    home_team: str
    away_team: str
    home_score: int
    away_score: int


class FootballResponse(FootballBase):
    """Schema for Football API responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
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
    team: Optional[str] = None  # Searches both home_team and away_team
    winner: Optional[str] = None
    year: Optional[int] = None
    week: Optional[int] = None


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
    total_matches: int
    unique_teams: int
    leagues: List[str]
    seasons: List[str]
    top_teams: List[dict]