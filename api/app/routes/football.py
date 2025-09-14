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
    """Get top 3 Football teams with investor metrics for dashboard ranking."""
    query = select(Football).order_by(desc(Football.wins)).limit(3)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Convert to frontend format with investor metrics
    top_teams = []
    for i, team in enumerate(teams):
        # Calculate points: 3 for win, 1 for draw
        points = (team.wins or 0) * 3 + (team.draws or 0)
        wins = team.wins or 0
        games = team.games_played or 1
        
        # Calculate investor metrics
        win_percentage = wins / games if games > 0 else 0
        base_engagement = random.randint(6000, 12000)  # Football typically has different engagement
        fan_engagement = base_engagement * (1 + win_percentage)
        sentiment_score = 55 + (win_percentage * 35) + random.randint(-10, 10)  # 55-100 range
        
        # Calculate sponsorship value score (weighted combination)
        sponsorship_value = (
            win_percentage * 40 +  # Performance weight
            (sentiment_score / 100) * 30 +  # Sentiment weight  
            min(fan_engagement / 12000, 1) * 30  # Engagement weight (capped at 1)
        )
        
        # Determine growth trend based on performance
        if win_percentage > 0.7:
            growth_trend = "up"
        elif win_percentage < 0.4:
            growth_trend = "down"
        else:
            growth_trend = "stable"
            
        top_teams.append(TopTeam(
            name=team.team or "Unknown Team",
            points=points,
            sponsorship_value_score=round(sponsorship_value, 1),
            growth_trend=growth_trend,
            fan_engagement=round(fan_engagement, 0),
            sentiment_score=round(sentiment_score, 1)
        ))
    
    return TopTeamsResponse(teams=top_teams)


@router.get("/team-mentions", response_model=TeamMentionsResponse)
async def get_football_team_mentions(db: AsyncSession = Depends(get_db)):
    """Get Football team mentions with engagement data for dashboard table."""
    query = select(Football).order_by(desc(Football.wins)).limit(10)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Convert to frontend format with enhanced metrics
    mentions_data = []
    sentiments = ["Positive", "Neutral", "Negative"]
    
    for team in teams:
        wins = team.wins or 0
        games = team.games_played or 1
        win_percentage = wins / games if games > 0 else 0
        
        # Generate metrics based on team performance
        base_mentions = random.randint(3000, 12000)
        mentions_count = int(base_mentions * (1 + win_percentage * 0.6))
        
        # Weekly change simulation based on performance
        if win_percentage > 0.65:
            weekly_change = f"+{random.randint(8, 30)}%"
        elif win_percentage < 0.35:
            weekly_change = f"-{random.randint(3, 18)}%"
        else:
            change = random.randint(-10, 15)
            weekly_change = f"+{change}%" if change >= 0 else f"{change}%"
        
        # Engagement level based on mentions
        if mentions_count > 10000:
            engagement_level = "High"
        elif mentions_count > 6000:
            engagement_level = "Medium"
        else:
            engagement_level = "Low"
            
        mentions_data.append(TeamMention(
            team=team.team or "Unknown Team",
            mentions=f"{mentions_count:,}",
            sentiment=random.choice(sentiments),
            weekly_change=weekly_change,
            engagement_level=engagement_level
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
    
    # Calculate enhanced metrics for investor analysis
    points = (team.wins or 0) * 3 + (team.draws or 0)
    wins = team.wins or 0
    games = team.games_played or 1
    losses = team.losses or 0
    win_percentage = wins / games if games > 0 else 0
    
    # Calculate investor metrics
    base_engagement = random.randint(8000, 16000)
    fan_engagement = base_engagement * (1 + win_percentage)
    sentiment_score = 55 + (win_percentage * 35) + random.randint(-10, 10)
    market_reach = int(fan_engagement * random.uniform(3.0, 5.0))  # Estimated total reach
    
    # Calculate sponsorship value score
    sponsorship_value = (
        win_percentage * 40 +
        (sentiment_score / 100) * 30 +
        min(fan_engagement / 16000, 1) * 30
    )
    
    # Determine growth trend
    if win_percentage > 0.7:
        growth_trend = "up"
    elif win_percentage < 0.4:
        growth_trend = "down"
    else:
        growth_trend = "stable"

    stats = TeamStats(
        team_name=team.team or team_name,
        games_played=games,
        wins=wins,
        losses=losses,
        points=points,
        win_percentage=round(win_percentage, 3),
        sponsorship_value_score=round(sponsorship_value, 1),
        fan_engagement=round(fan_engagement, 0),
        sentiment_score=round(sentiment_score, 1),
        growth_trend=growth_trend,
        market_reach=market_reach
    )
    
    return TeamStatsResponse(stats=stats)