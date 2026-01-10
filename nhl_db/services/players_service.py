from typing import Any, Dict, List, Optional, Set, Tuple
import logging

from ..clients.nhl_web_client import fetch_roster
from ..db import get_db_connection
from ..mappers.players import to_player_rows
from ..repositories.players_repo import upsert_players

logger = logging.getLogger(__name__)


def _get_active_teams_from_db() -> List[Tuple[int, str]]:
    sql = "SELECT teamId, teamAbbrev FROM teams WHERE teamIsActive = 1 AND teamAbbrev IS NOT NULL"
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        out: List[Tuple[int, str]] = []
        for row in cur.fetchall():
            out.append((int(row[0]), str(row[1])))
        cur.close()
        return out
    finally:
        conn.close()


def sync_players_roster(season: str, teams_filter: Optional[str] = None) -> int:
    allow: Optional[Set[str]] = None
    if teams_filter:
        allow = {t.strip().upper() for t in teams_filter.split(',') if t.strip()}

    team_rows = _get_active_teams_from_db()
    total = 0
    for team_id, tri in team_rows:
        if allow and tri.upper() not in allow:
            continue
        try:
            roster = fetch_roster(tri, season, team_id)
            rows = to_player_rows(roster, team_id)
            upsert_players(rows)
            total += len(rows)
            print(f"Synced {len(rows)} players for {tri} ({team_id}).")
        except Exception as e:
            logger.error(f"Error syncing players for team {tri} (team_id={team_id}): {e}", exc_info=True)
            raise
    return total


