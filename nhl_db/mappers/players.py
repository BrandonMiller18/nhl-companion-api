from typing import Any, Dict, List, Tuple


def to_player_rows(roster: List[Dict[str, Any]], team_id: int) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []
    for p in roster:
        try:
            pid = int(p.get("id"))
        except Exception:
            continue
        # Prefer per-player team id if present in the payload (e.g., Records API)
        try:
            player_team_id = int(p.get("playerTeamId")) if p.get("playerTeamId") is not None else team_id
        except Exception:
            player_team_id = team_id
        fn = p.get("firstName")
        if isinstance(fn, dict):
            first = fn.get("default") or next(iter(fn.values()), None)
        else:
            first = fn
        ln = p.get("lastName")
        if isinstance(ln, dict):
            last = ln.get("default") or next(iter(ln.values()), None)
        else:
            last = ln
        try:
            number = int(p.get("sweaterNumber")) if p.get("sweaterNumber") is not None else None
        except Exception:
            number = None
        position = p.get("positionCode")
        headshot = p.get("headshot")
        birth_city_block = p.get("birthCity")
        if isinstance(birth_city_block, dict):
            home_city = birth_city_block.get("default") or next(iter(birth_city_block.values()), None)
        else:
            home_city = None
        home_country = p.get("birthCountry")
        rows.append((
            pid,
            player_team_id,
            first or "",
            last or "",
            number,
            position,
            headshot,
            home_city,
            home_country,
        ))
    return rows


