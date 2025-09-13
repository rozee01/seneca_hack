from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import Optional, List
import math

from ..database import get_db
from ..models import Football
from ..schemas import (
    FootballResponse, 
    FootballList, 
    FootballStats
)

router = APIRouter(prefix="/football", tags=["Football"])


@router.get("/", response_model=FootballList)
async def get_football_teams(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    league: Optional[str] = Query(None, description="Filter by league"),
    season: Optional[str] = Query(None, description="Filter by season"),
    team: Optional[str] = Query(None, description="Filter by team name"),
    league_name: Optional[str] = Query(None, description="Filter by league name"),
    franchise: Optional[str] = Query(None, description="Filter by franchise"),
    sport: Optional[str] = Query(None, description="Filter by sport"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of football team season statistics with optional filters.
    """
    # Build base query
    query = select(Football)
    
    # Apply filters
    if league:
        query = query.where(Football.league.ilike(f"%{league}%"))
    
    if season:
        query = query.where(Football.season.ilike(f"%{season}%"))
    
    if team:
        query = query.where(Football.team.ilike(f"%{team}%"))
        
    if league_name:
        query = query.where(Football.league_name.ilike(f"%{league_name}%"))
        
    if franchise:
        query = query.where(Football.franchise.ilike(f"%{franchise}%"))
        
    if sport:
        query = query.where(Football.sport.ilike(f"%{sport}%"))
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Order by season_rank (best teams first)
    query = query.order_by(Football.season_rank.asc())
    
    # Execute query
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return FootballList(
        items=teams,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/team/{season}/{league}/{team_name}", response_model=FootballResponse)
async def get_football_team(
    season: str,
    league: str,
    team_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific football team's season statistics.
    """
    query = select(Football).where(
        and_(
            Football.season == season,
            Football.league == league,
            Football.team == team_name
        )
    )
    result = await db.execute(query)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(status_code=404, detail="Football team season data not found")
    
    return team


@router.get("/stats/summary", response_model=FootballStats)
async def get_football_stats(db: AsyncSession = Depends(get_db)):
    """
    Get football statistics summary.
    """
    # Total teams
    total_teams_query = select(func.count())
    total_teams = await db.scalar(total_teams_query.select_from(Football))
    
    # Leagues
    leagues_query = select(func.distinct(Football.league)).where(Football.league.is_not(None))
    leagues_result = await db.execute(leagues_query)
    leagues = [l[0] for l in leagues_result.fetchall()]
    
    # Seasons
    seasons_query = select(func.distinct(Football.season)).where(Football.season.is_not(None))
    seasons_result = await db.execute(seasons_query)
    seasons = [s[0] for s in seasons_result.fetchall()]
    
    # Sports
    sports_query = select(func.distinct(Football.sport)).where(Football.sport.is_not(None))
    sports_result = await db.execute(sports_query)
    sports = [s[0] for s in sports_result.fetchall()]
    
    # Top teams by win percentage
    top_teams = []
    if total_teams > 0:
        top_teams_query = select(
            Football.team,
            Football.league_name,
            Football.season,
            Football.win_percentage,
            Football.wins,
            Football.losses,
            Football.draws
        ).where(
            Football.win_percentage.is_not(None)
        ).order_by(
            Football.win_percentage.desc()
        ).limit(10)
        
        top_teams_result = await db.execute(top_teams_query)
        top_teams = [
            {
                "team": row.team, 
                "league": row.league_name,
                "season": row.season,
                "win_percentage": row.win_percentage,
                "wins": row.wins,
                "losses": row.losses,
                "draws": row.draws
            } 
            for row in top_teams_result.fetchall()
        ]
    
    return FootballStats(
        total_teams=total_teams or 0,
        leagues=leagues,
        seasons=seasons,
        sports=sports,
        top_teams=top_teams
    )


@router.get("/leagues/list")
async def get_leagues(db: AsyncSession = Depends(get_db)):
    """
    Get list of all leagues.
    """
    query = select(func.distinct(Football.league)).where(Football.league.is_not(None))
    result = await db.execute(query)
    leagues = [l[0] for l in result.fetchall()]
    return {"leagues": sorted(leagues)}


@router.get("/seasons/list")
async def get_seasons(db: AsyncSession = Depends(get_db)):
    """
    Get list of all seasons.
    """
    query = select(func.distinct(Football.season)).where(Football.season.is_not(None))
    result = await db.execute(query)
    seasons = [s[0] for s in result.fetchall()]
    return {"seasons": sorted(seasons)}


@router.get("/teams/search")
async def search_teams(
    q: str = Query(..., min_length=2, description="Search query for team names"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for teams by name.
    """
    query = select(Football.team).where(
        Football.team.ilike(f"%{q}%")
    ).distinct().limit(limit)
    
    result = await db.execute(query)
    teams = [t[0] for t in result.fetchall() if t[0]]
    
    return {"teams": sorted(teams)}


@router.get("/team/{team_name}/history")
async def get_team_history(
    team_name: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    league: Optional[str] = Query(None, description="Filter by league"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all season history for a specific team.
    """
    query = select(Football).where(Football.team.ilike(f"%{team_name}%"))
    
    if league:
        query = query.where(Football.league.ilike(f"%{league}%"))
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Order by season (most recent first)
    query = query.order_by(Football.season.desc())
    
    # Execute query
    result = await db.execute(query)
    seasons = result.scalars().all()
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return FootballList(
        items=seasons,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/league/{league_name}/standings")
async def get_league_standings(
    league_name: str,
    season: Optional[str] = Query(None, description="Season filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get standings for a league in a specific season.
    """
    # Build query for teams in the league
    query = select(Football).where(Football.league.ilike(f"%{league_name}%"))
    
    if season:
        query = query.where(Football.season == season)
    
    # Order by season rank (best to worst)
    query = query.order_by(Football.season_rank.asc())
    
    result = await db.execute(query)
    teams = result.scalars().all()
    
    if not teams:
        raise HTTPException(status_code=404, detail="No teams found for this league/season")
    
    # Format standings
    standings = []
    for team in teams:
        standings.append({
            "rank": team.season_rank,
            "team": team.team,
            "franchise": team.franchise,
            "games_played": team.games_played,
            "wins": team.wins,
            "losses": team.losses,
            "draws": team.draws,
            "win_percentage": team.win_percentage,
            "goals_scored": team.goals_scored,
            "goals_conceded": team.goals_conceded,
            "point_differential": team.point_differential
        })
    
    return {
        "league": league_name,
        "season": season,
        "standings": standings
    }