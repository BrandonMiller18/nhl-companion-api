from typing import Any, Dict, List
import logging

from ..clients.records_client import fetch_franchises
from ..mappers.teams import to_team_rows
from ..repositories.teams_repo import upsert_teams

logger = logging.getLogger(__name__)


def sync_teams_records() -> int:
    try:
        franchises: List[Dict[str, Any]] = fetch_franchises()
        rows = to_team_rows(franchises)
        upsert_teams(rows)
        return len(rows)
    except Exception as e:
        logger.error(f"Error syncing teams from Records API: {e}", exc_info=True)
        raise


