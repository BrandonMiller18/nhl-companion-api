import argparse

from ..services.players_service import sync_players_roster


def _cmd_sync_players_roster(args: argparse.Namespace) -> None:
    total = sync_players_roster(args.season, teams_filter=args.teams)
    print(f"Finished syncing {total} players across active teams.")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("sync-players-roster", help="Import players via NHL roster per team and season")
    p.add_argument("season", help="Season in YYYYYYYY format, e.g. 20252026")
    p.add_argument("--teams", help="Optional comma-separated triCodes to limit (e.g. 'SEA,VGK')", default=None)
    p.set_defaults(func=_cmd_sync_players_roster)


