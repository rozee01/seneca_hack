"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# NBA Schemas
class NbaBase(BaseModel):
    """Base NBA schema with common fields matching table structure."""
    season: Optional[str] = None
    league: Optional[str] = None
    league_name: Optional[str] = None
    team_id: Optional[str] = None
    franchise: Optional[str] = None
    games_played: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    win_percentage: Optional[float] = None
    goals_scored: Optional[int] = None  # total_points_scored in NBA context
    goals_conceded: Optional[int] = None  # total_points_conceded in NBA context
    point_differential: Optional[float] = None
    sport: Optional[str] = None
    season_rank: Optional[int] = None


class NbaCreate(NbaBase):
    """Schema for creating NBA records."""
    season: str
    league: str
    team_id: str
    games_played: int
    wins: int
    losses: int


class NbaResponse(NbaBase):
    """Schema for NBA API responses."""
    season: str
    league: str
    team_id: str
    
    class Config:
        from_attributes = True


class NbaList(BaseModel):
    """Schema for paginated Nba list responses."""
    items: List[NbaResponse]
    total: int
    page: int
    size: int
    pages: int


# Football Schemas
class FootballBase(BaseModel):
    """Base Football schema with common fields matching table structure."""
    season: Optional[str] = None
    league: Optional[str] = None
    league_name: Optional[str] = None
    team: Optional[str] = None
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
class NbaFilters(BaseModel):
    """Filters for NBA data queries."""
    season: Optional[str] = None
    league: Optional[str] = None
    team_id: Optional[str] = None
    franchise: Optional[str] = None
    min_wins: Optional[int] = None


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
class NbaStats(BaseModel):
    """NBA statistics summary."""
    total_teams: int
    unique_seasons: int
    unique_franchises: int
    average_wins: float
    average_losses: float
    average_win_percentage: float
    average_points_scored: float
    average_points_conceded: float


class FootballStats(BaseModel):
    """Football statistics summary."""
    total_teams: int
    leagues: List[str]
    seasons: List[str]
    sports: List[str]
    top_teams: List[dict]