from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def to_game_rows_from_schedule(games: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []
    for g in games:
        try:
            game_id = int(g.get("id"))
        except Exception:
            continue
        season = int(g.get("season")) if g.get("season") is not None else 0
        game_type = int(g.get("gameType")) if g.get("gameType") is not None else 0
        start_utc = g.get("startTimeUTC")
        dt_utc: Optional[str] = None
        if isinstance(start_utc, str) and start_utc:
            try:
                dt_utc = datetime.fromisoformat(start_utc.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                dt_utc = None
        venue = None
        if isinstance(g.get("venue"), dict):
            venue = g["venue"].get("default")
        home_team_id = int((g.get("homeTeam") or {}).get("id", 0))
        away_team_id = int((g.get("awayTeam") or {}).get("id", 0))
        game_state = g.get("gameState")
        home_score = int((g.get("homeTeam") or {}).get("score", 0)) if (g.get("homeTeam") or {}).get("score") is not None else 0
        away_score = int((g.get("awayTeam") or {}).get("score", 0)) if (g.get("awayTeam") or {}).get("score") is not None else 0
        rows.append((
            game_id,
            season,
            game_type,
            dt_utc,
            venue,
            home_team_id,
            away_team_id,
            game_state,
            home_score,
            away_score
        ))
    return rows


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def derive_game_fields_from_gamecenter(landing: Dict[str, Any], box: Dict[str, Any]) -> Tuple[Optional[str], Optional[int], Optional[str], int, int, int, int]:
    game_state = landing.get("gameState") or box.get("gameState")

    period: Optional[int] = None
    pd = landing.get("periodDescriptor") or {}
    if isinstance(pd, dict):
        pnum = pd.get("number")
        try:
            period = int(pnum) if pnum is not None else None
        except Exception:
            period = None

    clock: Optional[str] = None
    raw_clock = landing.get("clock")
    if isinstance(raw_clock, dict):
        clock = raw_clock.get("timeRemaining") or raw_clock.get("displayValue") or str(raw_clock)
    elif raw_clock is not None:
        clock = str(raw_clock)
    elif isinstance(pd, dict):
        tr = pd.get("timeRemaining")
        if tr is not None:
            clock = str(tr)

    home = (box.get("homeTeam") or landing.get("homeTeam") or {})
    away = (box.get("awayTeam") or landing.get("awayTeam") or {})

    home_score = _safe_int(home.get("score")) if home.get("score") is not None else 0
    away_score = _safe_int(away.get("score")) if away.get("score") is not None else 0
    home_sog = _safe_int(home.get("sog")) if home.get("sog") is not None else 0
    away_sog = _safe_int(away.get("sog")) if away.get("sog") is not None else 0

    return (game_state, period, clock, home_score, away_score, home_sog, away_sog)


