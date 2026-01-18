from typing import Any, Dict, List, Tuple
import logging

from ..db import get_db_connection

logger = logging.getLogger(__name__)


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


