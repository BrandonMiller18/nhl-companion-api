from typing import Any, Dict, List, Optional

import logging
import requests

from ..config import RECORDS_BASE

logger = logging.getLogger(__name__)


def get_configured_session() -> requests.Session:
    """
    Import and use the configured session from nhl_web_client.
    This avoids circular imports while maintaining a single source of truth.
    """
    from .nhl_web_client import get_configured_session as _get_configured_session
    return _get_configured_session()


def fetch_franchises(session: Optional[requests.Session] = None) -> List[Dict[str, Any]]:
    session = session or get_configured_session()
    includes = (
        "include=teams.id&include=teams.active&include=teams.triCode&include=teams.placeName"
        "&include=teams.commonName&include=teams.fullName&include=teams.logos"
        "&include=teams.conference.name&include=teams.division.name"
        "&include=teams.franchiseTeam.firstSeason.id&include=teams.franchiseTeam.lastSeason.id"
        "&include=teams.franchiseTeam.teamCommonName"
    )
    url = f"{RECORDS_BASE}/franchise?{includes}"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json() or {}
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching franchises from Records API, URL={url}: {e}", exc_info=True)
        raise



def fetch_players_by_team(team_id: int, session: Optional[requests.Session] = None) -> List[Dict[str, Any]]:
    session = session or get_configured_session()
    url = f"{RECORDS_BASE}/player/byTeam/{team_id}"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json() or {}
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching players for team_id={team_id} from Records API, URL={url}: {e}", exc_info=True)
        raise

