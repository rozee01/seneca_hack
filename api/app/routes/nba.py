"""
Minimal NBA routes for frontend requirements only.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List
import random

from ..database import get_db
from ..models import Nba
from ..schemas import TopTeamsResponse, TeamMentionsResponse, TeamStatsResponse, TopTeam, TeamMention, TeamStats

router = APIRouter(prefix="/nba", tags=["NBA"])


@router.get("/top-teams", response_model=TopTeamsResponse)
async def get_top_nba_teams(db: AsyncSession = Depends(get_db)):
    """Get top 3 NBA teams for dashboard ranking."""
    query = select(Nba).order_by(desc(Nba.wins)).limit(3)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Convert to frontend format
    top_teams = []
    for team in teams:
        # Calculate points based on wins (simple formula)
        points = (team.wins or 0) * 2 + (team.draws or 0)
        top_teams.append(TopTeam(
            name=team.franchise or team.team_id or "Unknown Team",
            points=points
        ))
    
    return TopTeamsResponse(teams=top_teams)


@router.get("/team-mentions", response_model=TeamMentionsResponse)
async def get_nba_team_mentions(db: AsyncSession = Depends(get_db)):
    """Get NBA team mentions data for dashboard table."""
    query = select(Nba).order_by(desc(Nba.wins)).limit(10)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Convert to frontend format with mock mentions and sentiment
    mentions_data = []
    sentiments = ["Positive", "Neutral", "Negative"]
    
    for team in teams:
        # Generate mock mentions count
        mentions_count = random.randint(5000, 15000)
        mentions_data.append(TeamMention(
            team=team.franchise or team.team_id or "Unknown Team",
            mentions=f"{mentions_count:,}",
            sentiment=random.choice(sentiments)
        ))
    
    return TeamMentionsResponse(data=mentions_data)


@router.get("/team/{team_name}", response_model=TeamStatsResponse)
async def get_nba_team_stats(team_name: str, db: AsyncSession = Depends(get_db)):
    """Get specific NBA team stats for team overview page."""
    # Try to find team by franchise name or team_id
    query = select(Nba).where(
        (Nba.franchise.ilike(f"%{team_name}%")) | 
        (Nba.team_id.ilike(f"%{team_name}%"))
    ).limit(1)
    
    result = await db.execute(query)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Calculate points
    points = (team.wins or 0) * 2 + (team.draws or 0)
    
    stats = TeamStats(
        team_name=team.franchise or team.team_id or team_name,
        games_played=team.games_played or 0,
        wins=team.wins or 0,
        losses=team.losses or 0,
        points=points
    )
    
    return TeamStatsResponse(stats=stats)