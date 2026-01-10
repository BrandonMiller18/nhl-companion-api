from typing import Any, Dict, List, Tuple
import logging

from ..db import get_db_connection

logger = logging.getLogger(__name__)


def upsert_teams(rows: List[Tuple[Any, ...]]) -> None:
    if not rows:
        return
    sql = (
        "INSERT INTO teams (teamId, teamName, teamCity, teamAbbrev, teamIsActive, teamLogoUrl) "
        "VALUES (%s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE teamName=VALUES(teamName), teamCity=VALUES(teamCity), teamAbbrev=VALUES(teamAbbrev), "
        "teamIsActive=VALUES(teamIsActive), teamLogoUrl=VALUES(teamLogoUrl)"
    )
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.executemany(sql, rows)
        except Exception as e:
            logger.error(f"Database error upserting {len(rows)} teams: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def get_all_teams() -> List[Dict[str, Any]]:
    """Fetch all teams from the database."""
    sql = """
        SELECT teamId, teamName, teamCity, teamAbbrev, teamIsActive, teamLogoUrl
        FROM teams
        ORDER BY teamName
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            logger.error(f"Database error fetching all teams: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


def get_active_teams() -> List[Dict[str, Any]]:
    """Fetch only active teams from the database."""
    sql = """
        SELECT teamId, teamName, teamCity, teamAbbrev, teamIsActive, teamLogoUrl
        FROM teams
        WHERE teamIsActive = TRUE
        ORDER BY teamName
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            logger.error(f"Database error fetching active teams: {e}", exc_info=True)
            raise
        finally:
            cur.close()
    finally:
        conn.close()


