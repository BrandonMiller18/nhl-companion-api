from typing import Any, Dict, List, Optional, Tuple


def pick_dark_logo_url(teams_entry: Dict[str, Any]) -> Optional[str]:
    logos = teams_entry.get("logos") or []
    best: Tuple[int, Optional[int], Optional[str]] = (-1, None, None)
    for lg in logos:
        if (lg.get("background") or "").lower() != "dark":
            continue
        start_season = int(lg.get("startSeason", -1)) if lg.get("startSeason") is not None else -1
        end_season = lg.get("endSeason")
        url = lg.get("secureUrl") or lg.get("url")
        if url is None:
            continue
        better = False
        if start_season > best[0]:
            better = True
        elif start_season == best[0]:
            prev_end = best[1]
            if prev_end is not None and end_season is None:
                better = True
        if better:
            best = (start_season, end_season, url)
    return best[2]


def to_team_rows(franchises: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []
    for fr in franchises:
        teams = fr.get("teams") or []
        for t in teams:
            try:
                team_id = int(t.get("id"))
            except Exception:
                continue
            common_name = t.get("commonName")
            if isinstance(common_name, dict):
                team_name = common_name.get("default") or next(iter(common_name.values()), None)
            else:
                team_name = common_name
            city = t.get("placeName")
            if isinstance(city, dict):
                team_city = city.get("default") or next(iter(city.values()), None)
            else:
                team_city = city
            abbrev = t.get("triCode")
            active = (t.get("active") or "").upper() == "Y"
            logo_url = pick_dark_logo_url(t)
            rows.append((team_id, team_name, team_city, abbrev, active, logo_url))
    return rows


