"""
Minimal Football routes for frontend requirements only.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List
import random

from ..database import get_db
from ..models import Football
from ..schemas import TopTeamsResponse, TeamMentionsResponse, TeamStatsResponse, TopTeam, TeamMention, TeamStats

router = APIRouter(prefix="/football", tags=["Football"])


@router.get("/top-teams", response_model=TopTeamsResponse)
async def get_top_football_teams(db: AsyncSession = Depends(get_db)):
    """Get top 3 Football teams for dashboard ranking."""
    query = select(Football).order_by(desc(Football.wins)).limit(3)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Convert to frontend format
    top_teams = []
    for team in teams:
        # Calculate points: 3 for win, 1 for draw
        points = (team.wins or 0) * 3 + (team.draws or 0)
        top_teams.append(TopTeam(
            name=team.team or "Unknown Team",
            points=points
        ))
    
    return TopTeamsResponse(teams=top_teams)


@router.get("/team-mentions", response_model=TeamMentionsResponse)
async def get_football_team_mentions(db: AsyncSession = Depends(get_db)):
    """Get Football team mentions data for dashboard table."""
    query = select(Football).order_by(desc(Football.wins)).limit(10)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Convert to frontend format with mock mentions and sentiment
    mentions_data = []
    sentiments = ["Positive", "Neutral", "Negative"]
    
    for team in teams:
        # Generate mock mentions count
        mentions_count = random.randint(3000, 12000)
        mentions_data.append(TeamMention(
            team=team.team or "Unknown Team",
            mentions=f"{mentions_count:,}",
            sentiment=random.choice(sentiments)
        ))
    
    return TeamMentionsResponse(data=mentions_data)


@router.get("/team/{team_name}", response_model=TeamStatsResponse)
async def get_football_team_stats(team_name: str, db: AsyncSession = Depends(get_db)):
    """Get specific Football team stats for team overview page."""
    # Try to find team by name
    query = select(Football).where(Football.team.ilike(f"%{team_name}%")).limit(1)
    
    result = await db.execute(query)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Calculate points: 3 for win, 1 for draw
    points = (team.wins or 0) * 3 + (team.draws or 0)
    
    stats = TeamStats(
        team_name=team.team or team_name,
        games_played=team.games_played or 0,
        wins=team.wins or 0,
        losses=team.losses or 0,
        points=points
    )
    
    return TeamStatsResponse(stats=stats)