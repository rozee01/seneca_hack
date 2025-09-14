"""
Minimal Pydantic schemas for frontend requirements only.
"""

from pydantic import BaseModel
from typing import List


# Simple team data for dashboard top teams
class TopTeam(BaseModel):
    """Top team with points for dashboard ranking."""
    name: str
    points: int
    
    class Config:
        from_attributes = True


# Team mentions data for dashboard table
class TeamMention(BaseModel):
    """Team mentions data for dashboard table."""
    team: str
    mentions: str
    sentiment: str
    
    class Config:
        from_attributes = True


# Simple team stats for team overview page
class TeamStats(BaseModel):
    """Basic team statistics for team page."""
    team_name: str
    games_played: int
    wins: int
    losses: int
    points: int
    
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