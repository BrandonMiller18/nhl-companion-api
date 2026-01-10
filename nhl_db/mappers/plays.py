from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def map_play(game_id: int, p: Dict[str, Any]) -> Tuple[Any, ...]:
    try:
        pid = str(game_id) + str(p.get("eventId", 0))
        play_id = int(pid)
        idx = p.get("sortOrder", 0)

        period = None
        time_str = None
        time_remaining = None
        pd = p.get("periodDescriptor") or {}
        if isinstance(pd, dict):
            period = pd.get("number")
            time_remaining = pd.get("timeRemaining")
            time_str = pd.get("timeElapsed") or time_remaining
        
        # Fallback to timeInPeriod if periodDescriptor doesn't have time data
        if not time_str:
            time_str = p.get("timeInPeriod")
        if not time_remaining:
            time_remaining = p.get("timeRemaining")
        
        # Provide defaults for NOT NULL fields
        if period is None:
            period = 0
        if not time_str:
            time_str = "00:00"
        if not time_remaining:
            time_remaining = "00:00"

        team_id = None
        if isinstance(p.get("team"), dict):
            team_id = p["team"].get("id")
        if team_id is None and isinstance(p.get("details"), dict):
            team_id = p["details"].get("eventOwnerTeamId")
        try:
            team_id = int(team_id) if team_id is not None else None
        except Exception as e:
            logger.error(f"Error parsing team_id for play in game_id={game_id}, eventId={p.get('eventId')}: {e}")
            team_id = None

        details = p.get("details") or {}
        primary_id = details.get("playerId") or details.get("shootingPlayerId") or details.get("scoringPlayerId") or details.get("hittingPlayerId") or details.get("winningPlayerId") or details.get("committedByPlayerId")
        opposing_player_id = details.get("losingPlayerId") or details.get("hitteePlayerId") or details.get("goalieInNetId") or details.get("blockingPlayerId") or details.get("drawnByPlayerId")

        secondary_id = details.get("assist1PlayerId")
        tertiary_id = details.get("assist2PlayerId")

        x = details.get("xCoord")
        y = details.get("yCoord")
        zone = details.get("zoneCode")
        ptype = p.get("typeDescKey") or (p.get("type") or {}).get("value")

        return (
            play_id,
            game_id,
            int(idx),
            team_id,
            primary_id,
            opposing_player_id,
            secondary_id,
            tertiary_id,
            period,
            time_str,
            time_remaining,
            ptype,
            zone,
            x,
            y,
        )
    except Exception as e:
        logger.error(f"Error mapping play data for game_id={game_id}, play={p}: {e}", exc_info=True)
        raise


