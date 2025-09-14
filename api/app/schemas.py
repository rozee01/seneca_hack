"""
Minimal Pydantic schemas for frontend requirements only.
"""

from pydantic import BaseModel
from typing import List


# Enhanced team data for investor-focused dashboard
class TopTeam(BaseModel):
    """Top team with points and investor metrics for dashboard ranking."""
    name: str
    points: int
    sponsorship_value_score: float  # Combined metric for investment appeal
    growth_trend: str  # "up", "down", "stable"
    fan_engagement: float  # Mentions per game or similar metric
    sentiment_score: float  # Average sentiment (0-100)
    
    class Config:
        from_attributes = True


# Enhanced team mentions data for investor insights
class TeamMention(BaseModel):
    """Team mentions data with engagement metrics for dashboard table."""
    team: str
    mentions: str
    sentiment: str
    weekly_change: str  # Percentage change in mentions
    engagement_level: str  # "High", "Medium", "Low"
    
    class Config:
        from_attributes = True


# Enhanced team stats for investor analysis
class TeamStats(BaseModel):
    """Comprehensive team statistics for investor evaluation."""
    team_name: str
    games_played: int
    wins: int
    losses: int
    points: int
    win_percentage: float
    sponsorship_value_score: float
    fan_engagement: float
    sentiment_score: float
    growth_trend: str
    market_reach: int  # Total mentions/followers estimate
    
    class Config:
        from_attributes = True


# Response models
class TopTeamsResponse(BaseModel):
    """Response for top teams endpoint."""
    teams: List[TopTeam]


class TeamMentionsResponse(BaseModel):
    """Response for team mentions endpoint."""
    data: List[TeamMention]


class TeamStatsResponse(BaseModel):
    """Response for individual team stats."""
    stats: TeamStats