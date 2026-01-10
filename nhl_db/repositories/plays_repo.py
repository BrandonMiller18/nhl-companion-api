from typing import Any, Dict, List, Tuple
import logging

from ..db import get_db_connection

logger = logging.getLogger(__name__)


def upsert_plays_from_pbp(game_id: int, pbp: Dict[str, Any], rows: List[Tuple[Any, ...]]) -> int:
    if not rows:
        return 0

    sql = (
        "INSERT INTO plays (playId, playGameId, playIndex, playTeamId, playPrimaryPlayerId, playLosingPlayerId, "
        "playSecondaryPlayerId, playTertiaryPlayerId, playPeriod, playTime, playTimeReamaining, "
        "playType, playZone, playXCoord, playYCoord) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE playTeamId=VALUES(playTeamId), playPrimaryPlayerId=VALUES(playPrimaryPlayerId), "
        "playLosingPlayerId=VALUES(playLosingPlayerId), playSecondaryPlayerId=VALUES(playSecondaryPlayerId), "
        "playTertiaryPlayerId=VALUES(playTertiaryPlayerId), playPeriod=VALUES(playPeriod), playTime=VALUES(playTime), "
        "playTimeReamaining=VALUES(playTimeReamaining), playType=VALUES(playType), "
        "playZone=VALUES(playZone), playXCoord=VALUES(playXCoord), playYCoord=VALUES(playYCoord)"
    )

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.executemany(sql, rows)
        except Exception as e:
            logger.error(f"Database error upserting {len(rows)} plays for game_id={game_id}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()
    return len(rows)


def upsert_plays_with_conn(conn, rows: List[Tuple[Any, ...]]) -> int:  # type: ignore[no-untyped-def]
    if not rows:
        return 0

    sql = (
        "INSERT INTO plays (playId, playGameId, playIndex, playTeamId, playPrimaryPlayerId, playLosingPlayerId, "
        "playSecondaryPlayerId, playTertiaryPlayerId, playPeriod, playTime, playTimeReamaining, "
        "playType, playZone, playXCoord, playYCoord) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE playTeamId=VALUES(playTeamId), playPrimaryPlayerId=VALUES(playPrimaryPlayerId), "
        "playLosingPlayerId=VALUES(playLosingPlayerId), playSecondaryPlayerId=VALUES(playSecondaryPlayerId), "
        "playTertiaryPlayerId=VALUES(playTertiaryPlayerId), playPeriod=VALUES(playPeriod), playTime=VALUES(playTime), "
        "playTimeReamaining=VALUES(playTimeReamaining), playType=VALUES(playType), "
        "playZone=VALUES(playZone), playXCoord=VALUES(playXCoord), playYCoord=VALUES(playYCoord)"
    )

    cur = conn.cursor()
    try:
        try:
            cur.executemany(sql, rows)
        except Exception as e:
            logger.error(f"Database error upserting {len(rows)} plays with connection: {e}", exc_info=True)
            raise
    finally:
        cur.close()
    return len(rows)


def get_plays_by_game(game_id: int) -> List[Dict[str, Any]]:
    """Fetch all play-by-play data for a specific game."""
    sql = """
        SELECT playId, playGameId, playIndex, playTeamId, playPrimaryPlayerId, playLosingPlayerId,
               playSecondaryPlayerId, playTertiaryPlayerId, playPeriod, playTime, playTimeReamaining,
               playType, playZone, playXCoord, playYCoord
        FROM plays
        WHERE playGameId = %s
        ORDER BY playPeriod, playIndex
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (game_id,))
            return cur.fetchall()
        except Exception as e:
            logger.error(f"Database error fetching plays for game {game_id}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


