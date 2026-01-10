from datetime import datetime, timedelta
import logging
from typing import List

from ..clients.nhl_web_client import fetch_schedule_for_date
from ..mappers.games import to_game_rows_from_schedule
from ..repositories.games_repo import upsert_games

logger = logging.getLogger(__name__)


def sync_schedule_dates(start: str, end: str) -> int:
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    if end_date < start_date:
        raise ValueError("end date must be >= start date")
    d = start_date
    total = 0
    while d <= end_date:
        ds = d.strftime("%Y-%m-%d")
        try:
            day_games = fetch_schedule_for_date(ds)
            rows = to_game_rows_from_schedule(day_games)
            upsert_games(rows)
            total += len(rows)
            print(f"{ds}: upserted {len(rows)} games")
        except Exception as e:
            logger.error(f"Error syncing schedule for date {ds}: {e}", exc_info=True)
            raise
        d += timedelta(days=1)
    return total


