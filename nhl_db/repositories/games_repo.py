from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime

import pytz

from ..db import get_db_connection

logger = logging.getLogger(__name__)


def upsert_games(rows: List[Tuple[Any, ...]]) -> None:
    if not rows:
        return
    sql = (
        "INSERT INTO games (gameId, gameSeason, gameType, gameDateTimeUtc, gameVenue, gameHomeTeamId, gameAwayTeamId, "
        "gameState, gameHomeScore, gameAwayScore) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE gameSeason=VALUES(gameSeason), gameType=VALUES(gameType), gameDateTimeUtc=VALUES(gameDateTimeUtc), "
        "gameVenue=VALUES(gameVenue), gameHomeTeamId=VALUES(gameHomeTeamId), gameAwayTeamId=VALUES(gameAwayTeamId), "
        "gameState=VALUES(gameState), gameHomeScore=VALUES(gameHomeScore), "
        "gameAwayScore=VALUES(gameAwayScore)"
    )
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.executemany(sql, rows)
        except Exception as e:
            logger.error(f"Database error upserting {len(rows)} games: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def update_game_fields(game_id: int, game_state: Optional[str], period: Optional[int], clock: Optional[str], home_score: int, away_score: int, home_sog: int, away_sog: int) -> None:
    sql = (
        "UPDATE games SET gameState=%s, gamePeriod=%s, gameClock=%s, gameHomeScore=%s, gameAwayScore=%s, "
        "gameHomeSOG=%s, gameAwaySOG=%s WHERE gameId=%s"
    )
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                sql,
                (
                    game_state,
                    period,
                    clock,
                    home_score,
                    away_score,
                    home_sog,
                    away_sog,
                    game_id,
                ),
            )
        except Exception as e:
            logger.error(f"Database error updating game fields for game_id={game_id}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def upsert_games_with_conn(conn, rows: List[Tuple[Any, ...]]) -> None:  # type: ignore[no-untyped-def]
    if not rows:
        return
    sql = (
        "INSERT INTO games (gameId, gameSeason, gameType, gameDateTimeUtc, gameVenue, gameHomeTeamId, gameAwayTeamId, "
        "gameState, gameHomeScore, gameAwayScore) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE gameSeason=VALUES(gameSeason), gameType=VALUES(gameType), gameDateTimeUtc=VALUES(gameDateTimeUtc), "
        "gameVenue=VALUES(gameVenue), gameHomeTeamId=VALUES(gameHomeTeamId), gameAwayTeamId=VALUES(gameAwayTeamId), "
        "gameState=VALUES(gameState), gameHomeScore=VALUES(gameHomeScore), gameAwayScore=VALUES(gameAwayScore)"
    )
    cur = conn.cursor()
    try:
        try:
            cur.executemany(sql, rows)
        except Exception as e:
            logger.error(f"Database error upserting {len(rows)} games with connection: {e}", exc_info=True)
            raise
    finally:
        cur.close()


def update_game_fields_with_conn(conn, game_id: int, game_state: Optional[str], period: Optional[int], clock: Optional[str], home_score: int, away_score: int, home_sog: int, away_sog: int) -> None:  # type: ignore[no-untyped-def]
    sql = (
        "UPDATE games SET gameState=%s, gamePeriod=%s, gameClock=%s, gameHomeScore=%s, gameAwayScore=%s, "
        "gameHomeSOG=%s, gameAwaySOG=%s WHERE gameId=%s"
    )
    cur = conn.cursor()
    try:
        try:
            cur.execute(
                sql,
                (
                    game_state,
                    period,
                    clock,
                    home_score,
                    away_score,
                    home_sog,
                    away_sog,
                    game_id,
                ),
            )
        except Exception as e:
            logger.error(f"Database error updating game fields with connection for game_id={game_id}: {e}", exc_info=True)
            raise
    finally:
        cur.close()


def get_games_by_date(date: str, timezone: str = "UTC") -> List[Dict[str, Any]]:
    """
    Fetch all games for a specific date in the specified timezone.
    
    Args:
        date: Date in YYYY-MM-DD format
        timezone: IANA timezone string (e.g., 'America/New_York', 'America/Los_Angeles')
    
    Returns:
        List of game dictionaries with team information
    """
    logger.info(f"=== get_games_by_date called with date={date}, timezone={timezone} ===")
    
    # Convert IANA timezone to UTC offset for MySQL
    try:
        tz = pytz.timezone(timezone)
        # Use a date in the middle of the target date to get the correct offset
        # (handles DST correctly)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        localized_date = tz.localize(target_date.replace(hour=12))
        offset_seconds = localized_date.utcoffset().total_seconds()
        offset_hours = int(offset_seconds / 3600)
        offset_minutes = int((abs(offset_seconds) % 3600) / 60)
        
        # Format as MySQL timezone offset: '+HH:MM' or '-HH:MM'
        if offset_seconds >= 0:
            tz_offset = f"+{offset_hours:02d}:{offset_minutes:02d}"
        else:
            tz_offset = f"{offset_hours:03d}:{offset_minutes:02d}"
        
        logger.info(f"Converting timezone {timezone} to offset {tz_offset} for date {date}")
    except Exception as e:
        logger.error(f"Error converting timezone {timezone}: {e}", exc_info=True)
        tz_offset = "+00:00"  # Fallback to UTC
    
    sql = """
        SELECT g.gameId, g.gameSeason, g.gameType, g.gameDateTimeUtc, g.gameVenue,
               g.gameHomeTeamId, g.gameAwayTeamId, g.gameState, g.gamePeriod, g.gameClock,
               g.gameHomeScore, g.gameAwayScore, g.gameHomeSOG, g.gameAwaySOG,
               ht.teamName as homeTeamName, ht.teamAbbrev as homeTeamAbbrev,
               at.teamName as awayTeamName, at.teamAbbrev as awayTeamAbbrev
        FROM games g
        JOIN teams ht ON g.gameHomeTeamId = ht.teamId
        JOIN teams at ON g.gameAwayTeamId = at.teamId
        WHERE DATE(CONVERT_TZ(g.gameDateTimeUtc, '+00:00', %s)) = %s
        ORDER BY g.gameDateTimeUtc
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (tz_offset, date))
            results = cur.fetchall()
            logger.info(f"Found {len(results)} games for date {date} in timezone {timezone} (offset {tz_offset})")
            return results
        except Exception as e:
            logger.error(f"Database error fetching games for date {date} in timezone {timezone}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def get_game_by_id(game_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single game by ID with team details."""
    sql = """
        SELECT g.gameId, g.gameSeason, g.gameType, g.gameDateTimeUtc, g.gameVenue,
               g.gameHomeTeamId, g.gameAwayTeamId, g.gameState, g.gamePeriod, g.gameClock,
               g.gameHomeScore, g.gameAwayScore, g.gameHomeSOG, g.gameAwaySOG,
               ht.teamName as homeTeamName, ht.teamAbbrev as homeTeamAbbrev,
               at.teamName as awayTeamName, at.teamAbbrev as awayTeamAbbrev
        FROM games g
        JOIN teams ht ON g.gameHomeTeamId = ht.teamId
        JOIN teams at ON g.gameAwayTeamId = at.teamId
        WHERE g.gameId = %s
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (game_id,))
            return cur.fetchone()
        except Exception as e:
            logger.error(f"Database error fetching game {game_id}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


