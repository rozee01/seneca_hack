from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, extract
from typing import Optional
import math

from ..database import get_db
from ..models import Nba
from ..schemas import (
    NbaResponse, 
    NbaList, 
    NbaStats
)

router = APIRouter(prefix="/nba", tags=["NBA"])


@router.get("/", response_model=NbaList)
async def get_nba_teams(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    season: Optional[str] = Query(None, description="Filter by season"),
    league: Optional[str] = Query(None, description="Filter by league"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    franchise: Optional[str] = Query(None, description="Filter by franchise"),
    min_wins: Optional[int] = Query(None, description="Minimum wins filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of NBA team statistics with optional filters.
    """
    # Build base query
    query = select(Nba)
    
    # Apply filters
    if season:
        query = query.where(Nba.season == season)
    
    if league:
        query = query.where(Nba.league.ilike(f"%{league}%"))
    
    if team_id:
        query = query.where(Nba.team_id.ilike(f"%{team_id}%"))
    
    if franchise:
        query = query.where(Nba.franchise.ilike(f"%{franchise}%"))
    
    if min_wins is not None:
        query = query.where(Nba.wins >= min_wins)
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Order by season and wins (most recent first, then by wins)
    query = query.order_by(Nba.season.desc(), Nba.wins.desc())
    
    # Execute query
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return NbaList(
        items=teams,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{season}/{league}/{team_id}", response_model=NbaResponse)
async def get_nba_team(
    season: str,
    league: str,
    team_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific NBA team's statistics by season, league, and team ID.
    """
    query = select(Nba).where(
        Nba.season == season,
        Nba.league == league,
        Nba.team_id == team_id
    )
    result = await db.execute(query)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(status_code=404, detail="NBA team statistics not found")
    
    return team


@router.get("/stats/summary", response_model=NbaStats)
async def get_nba_stats(db: AsyncSession = Depends(get_db)):
    """
    Get NBA statistics summary.
    """
    # Total teams
    total_teams_query = select(func.count()).select_from(Nba)
    total_teams = await db.scalar(total_teams_query)
    
    # Unique seasons
    seasons_query = select(func.count(func.distinct(Nba.season)))
    unique_seasons = await db.scalar(seasons_query) or 0
    
    # Unique franchises
    franchises_query = select(func.count(func.distinct(Nba.franchise)))
    unique_franchises = await db.scalar(franchises_query) or 0
    
    # Average stats
    avg_stats_query = select(
        func.avg(Nba.wins).label('avg_wins'),
        func.avg(Nba.losses).label('avg_losses'),
        func.avg(Nba.win_percentage).label('avg_win_percentage'),
        func.avg(Nba.goals_scored).label('avg_points_scored'),
        func.avg(Nba.goals_conceded).label('avg_points_conceded')
    )
    avg_stats = await db.execute(avg_stats_query)
    stats = avg_stats.first()
    
    return {
        "total_teams": total_teams,
        "unique_seasons": unique_seasons,
        "unique_franchises": unique_franchises,
        "average_wins": round(stats.avg_wins, 2) if stats.avg_wins else 0,
        "average_losses": round(stats.avg_losses, 2) if stats.avg_losses else 0,
        "average_win_percentage": round(stats.avg_win_percentage, 2) if stats.avg_win_percentage else 0,
        "average_points_scored": round(stats.avg_points_scored, 2) if stats.avg_points_scored else 0,
        "average_points_conceded": round(stats.avg_points_conceded, 2) if stats.avg_points_conceded else 0
    }


@router.get("/seasons", response_model=list[str])
async def get_seasons(db: AsyncSession = Depends(get_db)):
    """Get list of available seasons."""
    query = select(func.distinct(Nba.season)).order_by(Nba.season.desc())
    result = await db.execute(query)
    seasons = [row[0] for row in result.fetchall()]
    return seasons


@router.get("/franchises", response_model=list[str])
async def get_franchises(db: AsyncSession = Depends(get_db)):
    """Get list of available franchises."""
    query = select(func.distinct(Nba.franchise)).where(Nba.franchise.is_not(None)).order_by(Nba.franchise)
    result = await db.execute(query)
    franchises = [row[0] for row in result.fetchall()]
    return franchises


@router.get("/season/{season}", response_model=NbaList)
async def get_season_standings(
    season: str,
    db: AsyncSession = Depends(get_db)
):
    """Get season standings for a specific season."""
    query = select(Nba).where(Nba.season == season).order_by(Nba.season_rank.asc())
    result = await db.execute(query)
    teams = result.scalars().all()
    
    if not teams:
        raise HTTPException(status_code=404, detail=f"No data found for season {season}")
    
    return NbaList(
        items=teams,
        total=len(teams),
        page=1,
        size=len(teams),
        pages=1
    )