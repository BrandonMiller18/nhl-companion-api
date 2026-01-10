"""API router with all endpoints for NHL Companion."""
import logging
from datetime import datetime
from typing import List, Optional

import pytz
from fastapi import APIRouter, Depends, HTTPException, Query, status

from nhl_db.repositories import games_repo, players_repo, plays_repo, teams_repo
from .auth import verify_token
from .models import GameDetailResponse, GameResponse, PlayerResponse, PlayResponse, TeamResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["nhl"])


@router.get("/teams", response_model=List[TeamResponse])
async def get_all_teams(token: str = Depends(verify_token)) -> List[TeamResponse]:
    """
    Get all teams.
    
    Returns a list of all NHL teams in the database.
    """
    try:
        teams = teams_repo.get_all_teams()
        return [TeamResponse(**team) for team in teams]
    except Exception as e:
        logger.error(f"Error fetching all teams: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch teams"
        )


@router.get("/teams/active", response_model=List[TeamResponse])
async def get_active_teams(token: str = Depends(verify_token)) -> List[TeamResponse]:
    """
    Get active teams only.
    
    Returns a list of currently active NHL teams.
    """
    try:
        teams = teams_repo.get_active_teams()
        return [TeamResponse(**team) for team in teams]
    except Exception as e:
        logger.error(f"Error fetching active teams: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch active teams"
        )


@router.get("/games", response_model=List[GameResponse])
async def get_games_by_date(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    timezone: str = Query("America/New_York", description="IANA timezone string (e.g., America/New_York)"),
    token: str = Depends(verify_token)
) -> List[GameResponse]:
    """
    Get games filtered by date and timezone.
    
    Returns all games scheduled for the specified date in the given timezone.
    If no date is provided, returns games for "today" in the specified timezone.
    
    Args:
        date: Optional date in YYYY-MM-DD format (e.g., 2024-01-15). If not provided, uses today.
        timezone: IANA timezone string (defaults to America/New_York for Eastern Time)
    """
    try:
        # Validate timezone by attempting to create it
        try:
            tz = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid timezone: {timezone}. Must be a valid IANA timezone string."
            )
        
        # If no date provided, calculate "today" in the specified timezone
        if date is None:
            now_in_tz = datetime.now(tz)
            date = now_in_tz.strftime("%Y-%m-%d")
            logger.info(f"No date provided, using today in {timezone}: {date}")
        
        # Fetch games for the date in the specified timezone
        games = games_repo.get_games_by_date(date, timezone)
        return [GameResponse(**game) for game in games]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching games for date {date} in timezone {timezone}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch games for date {date}"
        )


@router.get("/teams/{team_id}/players", response_model=List[PlayerResponse])
async def get_players_by_team(
    team_id: int,
    token: str = Depends(verify_token)
) -> List[PlayerResponse]:
    """
    Get players by team.
    
    Returns all players for the specified team.
    
    Args:
        team_id: The team ID to fetch players for
    """
    try:
        players = players_repo.get_players_by_team(team_id)
        if not players:
            logger.info(f"No players found for team {team_id}")
            return []
        return [PlayerResponse(**player) for player in players]
    except Exception as e:
        logger.error(f"Error fetching players for team {team_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch players for team {team_id}"
        )


@router.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player_by_id(
    player_id: int,
    token: str = Depends(verify_token)
) -> PlayerResponse:
    """
    Get player by ID.
    
    Returns detailed information for a specific player.
    
    Args:
        player_id: The player ID to fetch details for
    """
    try:
        player = players_repo.get_player_by_id(player_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player {player_id} not found"
            )
        return PlayerResponse(**player)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player {player_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch player {player_id}"
        )


@router.get("/games/{game_id}", response_model=GameDetailResponse)
async def get_game_detail(
    game_id: int,
    token: str = Depends(verify_token)
) -> GameDetailResponse:
    """
    Get game details and play-by-play data.
    
    Returns comprehensive game information including all play-by-play events.
    
    Args:
        game_id: The game ID to fetch details for
    """
    try:
        # Fetch game details
        game = games_repo.get_game_by_id(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game {game_id} not found"
            )
        
        # Fetch play-by-play data
        plays = plays_repo.get_plays_by_game(game_id)
        
        return GameDetailResponse(
            game=GameResponse(**game),
            plays=[PlayResponse(**play) for play in plays]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching game detail for game {game_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch game detail for game {game_id}"
        )

