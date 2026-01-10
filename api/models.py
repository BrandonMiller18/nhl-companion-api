"""Pydantic models for API responses."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TeamResponse(BaseModel):
    """Team data structure."""
    teamId: int = Field(..., description="Unique team identifier")
    teamName: str = Field(..., description="Team name")
    teamCity: Optional[str] = Field(None, description="Team city")
    teamAbbrev: Optional[str] = Field(None, description="Team abbreviation")
    teamIsActive: bool = Field(..., description="Whether the team is currently active")
    teamLogoUrl: Optional[str] = Field(None, description="URL to team logo")

    class Config:
        from_attributes = True


class PlayerResponse(BaseModel):
    """Player data structure."""
    playerId: int = Field(..., description="Unique player identifier")
    playerTeamId: Optional[int] = Field(None, description="Team ID the player belongs to")
    playerFirstName: str = Field(..., description="Player first name")
    playerLastName: str = Field(..., description="Player last name")
    playerNumber: Optional[int] = Field(None, description="Player jersey number")
    playerPosition: Optional[str] = Field(None, description="Player position")
    playerHeadshotUrl: Optional[str] = Field(None, description="URL to player headshot")
    playerHomeCity: Optional[str] = Field(None, description="Player home city")
    playerHomeCountry: Optional[str] = Field(None, description="Player home country")

    class Config:
        from_attributes = True


class GameResponse(BaseModel):
    """Game data structure."""
    gameId: int = Field(..., description="Unique game identifier")
    gameSeason: int = Field(..., description="Season year")
    gameType: int = Field(..., description="Game type (regular season, playoffs, etc.)")
    gameDateTimeUtc: datetime = Field(..., description="Game date and time in UTC")
    gameVenue: Optional[str] = Field(None, description="Game venue name")
    gameHomeTeamId: int = Field(..., description="Home team ID")
    gameAwayTeamId: int = Field(..., description="Away team ID")
    gameState: str = Field(..., description="Game state (scheduled, in_progress, final, etc.)")
    gamePeriod: Optional[int] = Field(None, description="Current period")
    gameClock: Optional[str] = Field(None, description="Current game clock")
    gameHomeScore: int = Field(..., description="Home team score")
    gameAwayScore: int = Field(..., description="Away team score")
    gameHomeSOG: int = Field(..., description="Home team shots on goal")
    gameAwaySOG: int = Field(..., description="Away team shots on goal")
    homeTeamName: Optional[str] = Field(None, description="Home team name")
    homeTeamAbbrev: Optional[str] = Field(None, description="Home team abbreviation")
    awayTeamName: Optional[str] = Field(None, description="Away team name")
    awayTeamAbbrev: Optional[str] = Field(None, description="Away team abbreviation")

    class Config:
        from_attributes = True


class PlayResponse(BaseModel):
    """Play-by-play data structure."""
    playId: int = Field(..., description="Unique play identifier")
    playGameId: int = Field(..., description="Game ID this play belongs to")
    playIndex: int = Field(..., description="Play index within the game")
    playTeamId: Optional[int] = Field(None, description="Team ID associated with the play")
    playPrimaryPlayerId: Optional[int] = Field(None, description="Primary player ID")
    playLosingPlayerId: Optional[int] = Field(None, description="Losing player ID (for faceoffs)")
    playSecondaryPlayerId: Optional[int] = Field(None, description="Secondary player ID")
    playTertiaryPlayerId: Optional[int] = Field(None, description="Tertiary player ID")
    playPeriod: int = Field(..., description="Period number")
    playTime: str = Field(..., description="Time in period (MM:SS)")
    playTimeReamaining: str = Field(..., description="Time remaining in period (MM:SS)")
    playType: str = Field(..., description="Type of play")
    playZone: Optional[int] = Field(None, description="Zone code")
    playXCoord: Optional[int] = Field(None, description="X coordinate on ice")
    playYCoord: Optional[int] = Field(None, description="Y coordinate on ice")

    class Config:
        from_attributes = True


class GameDetailResponse(BaseModel):
    """Combined game and play-by-play data."""
    game: GameResponse = Field(..., description="Game details")
    plays: List[PlayResponse] = Field(..., description="Play-by-play data for the game")

    class Config:
        from_attributes = True

