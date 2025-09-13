"""
API routes for NBA data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, extract
from typing import Optional, List
import math

from ..database import get_db
from ..models import Tennis
from ..schemas import (
    TennisResponse, 
    TennisList, 
    TennisFilters, 
    PaginationParams,
    TennisStats
)

router = APIRouter(prefix="/nba", tags=["NBA"])


@router.get("/", response_model=TennisList)
async def get_tennis_matches(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    tournament: Optional[str] = Query(None, description="Filter by tournament"),
    surface: Optional[str] = Query(None, description="Filter by surface"),
    player: Optional[str] = Query(None, description="Filter by player name"),
    country: Optional[str] = Query(None, description="Filter by player country"),
    year: Optional[int] = Query(None, description="Filter by year"),
    winner: Optional[str] = Query(None, description="Filter by winner"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of tennis matches with optional filters.
    """
    # Build base query
    query = select(Tennis)
    
    # Apply filters
    if tournament:
        query = query.where(Tennis.tournament.ilike(f"%{tournament}%"))
    
    if surface:
        query = query.where(Tennis.surface.ilike(f"%{surface}%"))
    
    if player:
        query = query.where(
            or_(
                Tennis.player1_name.ilike(f"%{player}%"),
                Tennis.player2_name.ilike(f"%{player}%")
            )
        )
    
    if country:
        query = query.where(
            or_(
                Tennis.player1_country.ilike(f"%{country}%"),
                Tennis.player2_country.ilike(f"%{country}%")
            )
        )
    
    if year:
        query = query.where(extract('year', Tennis.date) == year)
    
    if winner:
        query = query.where(Tennis.winner.ilike(f"%{winner}%"))
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # Order by date (most recent first)
    query = query.order_by(Tennis.date.desc())
    
    # Execute query
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return TennisList(
        items=matches,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{match_id}", response_model=TennisResponse)
async def get_tennis_match(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific tennis match by ID.
    """
    query = select(Tennis).where(Tennis.id == match_id)
    result = await db.execute(query)
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="Tennis match not found")
    
    return match


@router.get("/stats/summary", response_model=TennisStats)
async def get_tennis_stats(db: AsyncSession = Depends(get_db)):
    """
    Get tennis statistics summary.
    """
    # Total matches
    total_matches_query = select(func.count(Tennis.id))
    total_matches = await db.scalar(total_matches_query)
    
    # Unique players (approximate count)
    unique_players_query = select(func.count(func.distinct(Tennis.player1_name))) + \
                          select(func.count(func.distinct(Tennis.player2_name)))
    unique_players = await db.scalar(unique_players_query) or 0
    
    # Tournaments
    tournaments_query = select(func.distinct(Tennis.tournament)).where(Tennis.tournament.is_not(None))
    tournaments_result = await db.execute(tournaments_query)
    tournaments = [t[0] for t in tournaments_result.fetchall()]
    
    # Surfaces
    surfaces_query = select(func.distinct(Tennis.surface)).where(Tennis.surface.is_not(None))
    surfaces_result = await db.execute(surfaces_query)
    surfaces = [s[0] for s in surfaces_result.fetchall()]
    
    # Top players by wins (simplified)
    top_players = []
    if total_matches > 0:
        top_players_query = select(
            Tennis.winner,
            func.count(Tennis.winner).label('wins')
        ).where(
            Tennis.winner.is_not(None)
        ).group_by(
            Tennis.winner
        ).order_by(
            func.count(Tennis.winner).desc()
        ).limit(10)
        
        top_players_result = await db.execute(top_players_query)
        top_players = [
            {"player": row.winner, "wins": row.wins} 
            for row in top_players_result.fetchall()
        ]
    
    return TennisStats(
        total_matches=total_matches or 0,
        unique_players=unique_players,
        tournaments=tournaments,
        surfaces=surfaces,
        top_players=top_players
    )


@router.get("/tournaments/list")
async def get_tournaments(db: AsyncSession = Depends(get_db)):
    """
    Get list of all tournaments.
    """
    query = select(func.distinct(Tennis.tournament)).where(Tennis.tournament.is_not(None))
    result = await db.execute(query)
    tournaments = [t[0] for t in result.fetchall()]
    return {"tournaments": sorted(tournaments)}


@router.get("/surfaces/list")
async def get_surfaces(db: AsyncSession = Depends(get_db)):
    """
    Get list of all court surfaces.
    """
    query = select(func.distinct(Tennis.surface)).where(Tennis.surface.is_not(None))
    result = await db.execute(query)
    surfaces = [s[0] for s in result.fetchall()]
    return {"surfaces": sorted(surfaces)}


@router.get("/players/search")
async def search_players(
    q: str = Query(..., min_length=2, description="Search query for player names"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for players by name.
    """
    # Search in both player1_name and player2_name
    player1_query = select(Tennis.player1_name).where(
        Tennis.player1_name.ilike(f"%{q}%")
    ).distinct()
    
    player2_query = select(Tennis.player2_name).where(
        Tennis.player2_name.ilike(f"%{q}%")
    ).distinct()
    
    # Execute both queries
    player1_result = await db.execute(player1_query)
    player2_result = await db.execute(player2_query)
    
    # Combine and deduplicate results
    all_players = set()
    all_players.update([p[0] for p in player1_result.fetchall() if p[0]])
    all_players.update([p[0] for p in player2_result.fetchall() if p[0]])
    
    # Sort and limit
    sorted_players = sorted(list(all_players))[:limit]
    
    return {"players": sorted_players}