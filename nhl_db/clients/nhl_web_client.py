from typing import Any, Dict, List, Optional

import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .records_client import fetch_players_by_team

from ..config import NHL_WEB_BASE

logger = logging.getLogger(__name__)


def get_configured_session() -> requests.Session:
    """
    Create a requests.Session with retry logic and connection pooling configured.
    
    This handles connection resets, timeouts, and transient server errors
    that occur during extended application runtime.
    
    Returns:
        A configured requests.Session with automatic retry capability.
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=0.5,  # Exponential backoff: 0.5s, 1s, 2s
        status_forcelist=[500, 502, 503, 504],  # Retry on server errors
        allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
        raise_on_status=False  # Don't raise on status, let status_forcelist handle it
    )
    
    # Create adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    # Mount adapter for both http and https
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_roster(tricode: str, season: str, team_id: int, session: Optional[requests.Session] = None) -> List[Dict[str, Any]]:
    session = session or get_configured_session()
    tri = (tricode or "").lower()
    # NHL Web roster (primary source)
    url = f"{NHL_WEB_BASE}/roster/{tri}/{season}"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json() or {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching roster for {tricode} (team_id={team_id}), URL={url}: {e}", exc_info=True)
        raise
    web_players: List[Dict[str, Any]] = []
    for group in ("forwards", "defensemen", "goalies"):
        web_players.extend(data.get(group, []) or [])

    # Build a set of player IDs present in NHL Web roster for dedupe
    web_ids = set()
    for p in web_players:
        try:
            web_ids.add(int(p.get("id")))
        except Exception:
            continue

    # Records API players (secondary source, fill only missing players)
    records_players = fetch_players_by_team(team_id, session=session)
    merged: List[Dict[str, Any]] = list(web_players)
    for rp in records_players:
        try:
            rid = int(rp.get("id"))
        except Exception:
            continue
        if rid in web_ids:
            # Prefer NHL Web data entirely when present
            continue
        # Map Records fields to NHL Web roster shape
        first_name = rp.get("firstName")
        last_name = rp.get("lastName")
        sweater = rp.get("sweaterNumber")
        position_code = rp.get("position")  # prefer "position" per mapping
        headshot = None  # Records has no headshot
        birth_city = rp.get("birthCity")
        birth_city_block: Optional[Dict[str, Any]] = {"default": birth_city} if birth_city else None
        birth_country = rp.get("birthCountry")
        current_team_id = rp.get("currentTeamId")
        mapped: Dict[str, Any] = {
            "id": rid,
            "firstName": first_name,
            "lastName": last_name,
            "sweaterNumber": sweater,
            "positionCode": position_code,
            "headshot": headshot,
            "birthCity": birth_city_block,
            "birthCountry": birth_country,
            # Provide per-player team id from Records to override when applicable
            "playerTeamId": current_team_id,
        }
        merged.append(mapped)

    return merged


def fetch_schedule_for_date(date_str: str, session: Optional[requests.Session] = None) -> List[Dict[str, Any]]:
    print(f"Fetching schedule for date: {date_str}...")
    session = session or get_configured_session()
    url = f"{NHL_WEB_BASE}/schedule/{date_str}"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json() or {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching schedule for date {date_str}, URL={url}: {e}", exc_info=True)
        raise
    games: List[Dict[str, Any]] = []
    for day in data.get("gameWeek", []) or []:
        for g in day.get("games", []) or []:
            games.append(g)
    return games


def fetch_game_landing(game_id: int, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    session = session or get_configured_session()
    url = f"{NHL_WEB_BASE}/gamecenter/{game_id}/landing"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json() or {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching game landing for game_id={game_id}, URL={url}: {e}", exc_info=True)
        raise


def fetch_game_boxscore(game_id: int, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    session = session or get_configured_session()
    url = f"{NHL_WEB_BASE}/gamecenter/{game_id}/boxscore"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json() or {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching game boxscore for game_id={game_id}, URL={url}: {e}", exc_info=True)
        raise


def fetch_game_pbp(game_id: int, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    session = session or get_configured_session()
    url = f"{NHL_WEB_BASE}/gamecenter/{game_id}/play-by-play"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json() or {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching game play-by-play for game_id={game_id}, URL={url}: {e}", exc_info=True)
        raise


