"""
API routes for Football data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, extract
from typing import Optional, List
import math

from ..database import get_db
from ..models import Football
from ..schemas import (
    FootballResponse, 
    FootballList, 
    FootballFilters, 
    PaginationParams,
    FootballStats
)

router = APIRouter(prefix="/football", tags=["Football"])


@router.get("/", response_model=FootballList)
async def get_football_matches(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    league: Optional[str] = Query(None, description="Filter by league"),
    season: Optional[str] = Query(None, description="Filter by season"),
    team: Optional[str] = Query(None, description="Filter by team name"),
    winner: Optional[str] = Query(None, description="Filter by winner (home/away/draw)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    week: Optional[int] = Query(None, description="Filter by week"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of football matches with optional filters.
    """
    # Build base query
    query = select(Football)
    
    # Apply filters
    if league:
        query = query.where(Football.league.ilike(f"%{league}%"))
    
    if season:
        query = query.where(Football.season.ilike(f"%{season}%"))
    
    if team:
        query = query.where(
            or_(
                Football.home_team.ilike(f"%{team}%"),
                Football.away_team.ilike(f"%{team}%")
            )
        )
    
    if winner:
        query = query.where(Football.winner.ilike(f"%{winner}%"))
    
    if year:
        query = query.where(extract('year', Football.date) == year)
    
    if week:
        query = query.where(Football.week == week)
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Order by date (most recent first)
    query = query.order_by(Football.date.desc())
    
    # Execute query
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return FootballList(
        items=matches,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{match_id}", response_model=FootballResponse)
async def get_football_match(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific football match by ID.
    """
    query = select(Football).where(Football.id == match_id)
    result = await db.execute(query)
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="Football match not found")
    
    return match


@router.get("/stats/summary", response_model=FootballStats)
async def get_football_stats(db: AsyncSession = Depends(get_db)):
    """
    Get football statistics summary.
    """
    # Total matches
    total_matches_query = select(func.count(Football.id))
    total_matches = await db.scalar(total_matches_query)
    
    # Unique teams (approximate count)
    unique_teams_query = select(func.count(func.distinct(Football.home_team))) + \
                        select(func.count(func.distinct(Football.away_team)))
    unique_teams = await db.scalar(unique_teams_query) or 0
    
    # Leagues
    leagues_query = select(func.distinct(Football.league)).where(Football.league.is_not(None))
    leagues_result = await db.execute(leagues_query)
    leagues = [l[0] for l in leagues_result.fetchall()]
    
    # Seasons
    seasons_query = select(func.distinct(Football.season)).where(Football.season.is_not(None))
    seasons_result = await db.execute(seasons_query)
    seasons = [s[0] for s in seasons_result.fetchall()]
    
    # Top teams by wins (home wins only for simplicity)
    top_teams = []
    if total_matches > 0:
        top_teams_query = select(
            Football.home_team,
            func.count(Football.home_team).label('home_wins')
        ).where(
            Football.winner == 'home',
            Football.home_team.is_not(None)
        ).group_by(
            Football.home_team
        ).order_by(
            func.count(Football.home_team).desc()
        ).limit(10)
        
        top_teams_result = await db.execute(top_teams_query)
        top_teams = [
            {"team": row.home_team, "home_wins": row.home_wins} 
            for row in top_teams_result.fetchall()
        ]
    
    return FootballStats(
        total_matches=total_matches or 0,
        unique_teams=unique_teams,
        leagues=leagues,
        seasons=seasons,
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
    # Search in both home_team and away_team
    home_team_query = select(Football.home_team).where(
        Football.home_team.ilike(f"%{q}%")
    ).distinct()
    
    away_team_query = select(Football.away_team).where(
        Football.away_team.ilike(f"%{q}%")
    ).distinct()
    
    # Execute both queries
    home_result = await db.execute(home_team_query)
    away_result = await db.execute(away_team_query)
    
    # Combine and deduplicate results
    all_teams = set()
    all_teams.update([t[0] for t in home_result.fetchall() if t[0]])
    all_teams.update([t[0] for t in away_result.fetchall() if t[0]])
    
    # Sort and limit
    sorted_teams = sorted(list(all_teams))[:limit]
    
    return {"teams": sorted_teams}


@router.get("/team/{team_name}/matches")
async def get_team_matches(
    team_name: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    season: Optional[str] = Query(None, description="Filter by season"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all matches for a specific team.
    """
    query = select(Football).where(
        or_(
            Football.home_team.ilike(f"%{team_name}%"),
            Football.away_team.ilike(f"%{team_name}%")
        )
    )
    
    if season:
        query = query.where(Football.season.ilike(f"%{season}%"))
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Order by date (most recent first)
    query = query.order_by(Football.date.desc())
    
    # Execute query
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return FootballList(
        items=matches,
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
    Get basic standings for a league (simplified version).
    This is a basic implementation - you might want to enhance it based on your needs.
    """
    # Build query for matches in the league
    query = select(Football).where(Football.league.ilike(f"%{league_name}%"))
    
    if season:
        query = query.where(Football.season.ilike(f"%{season}%"))
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Calculate basic standings
    standings = {}
    
    for match in matches:
        # Home team
        if match.home_team not in standings:
            standings[match.home_team] = {"played": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0}
        
        # Away team
        if match.away_team not in standings:
            standings[match.away_team] = {"played": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0}
        
        # Update match counts
        standings[match.home_team]["played"] += 1
        standings[match.away_team]["played"] += 1
        
        # Update results
        if match.winner == "home":
            standings[match.home_team]["wins"] += 1
            standings[match.home_team]["points"] += 3
            standings[match.away_team]["losses"] += 1
        elif match.winner == "away":
            standings[match.away_team]["wins"] += 1
            standings[match.away_team]["points"] += 3
            standings[match.home_team]["losses"] += 1
        elif match.winner == "draw":
            standings[match.home_team]["draws"] += 1
            standings[match.home_team]["points"] += 1
            standings[match.away_team]["draws"] += 1
            standings[match.away_team]["points"] += 1
    
    # Sort by points (descending)
    sorted_standings = sorted(
        [{"team": team, **stats} for team, stats in standings.items()],
        key=lambda x: x["points"],
        reverse=True
    )
    
    return {
        "league": league_name,
        "season": season,
        "standings": sorted_standings
    }