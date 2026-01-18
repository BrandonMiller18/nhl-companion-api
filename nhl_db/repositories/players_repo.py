from typing import Any, Dict, List, Optional, Tuple
import logging

from ..db import get_db_connection

logger = logging.getLogger(__name__)


def get_players_by_team(team_id: int) -> List[Dict[str, Any]]:
    """Fetch all players for a specific team."""
    sql = """
        SELECT playerId, playerTeamId, playerFirstName, playerLastName, playerNumber,
               playerPosition, playerHeadshotUrl, playerHomeCity, playerHomeCountry, playerIsActive
        FROM players
        WHERE playerTeamId = %s
        ORDER BY playerLastName, playerFirstName
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (team_id,))
            return cur.fetchall()
        except Exception as e:
            logger.error(f"Database error fetching players for team {team_id}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def get_player_by_id(player_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single player by player ID."""
    sql = """
        SELECT playerId, playerTeamId, playerFirstName, playerLastName, playerNumber,
               playerPosition, playerHeadshotUrl, playerHomeCity, playerHomeCountry, playerIsActive
        FROM players
        WHERE playerId = %s
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql, (player_id,))
            return cur.fetchone()
        except Exception as e:
            logger.error(f"Database error fetching player {player_id}: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


