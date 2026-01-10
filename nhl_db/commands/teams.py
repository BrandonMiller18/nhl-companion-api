import argparse

from ..services.teams_service import sync_teams_records


def _cmd_sync_teams_records(_: argparse.Namespace) -> None:
    count = sync_teams_records()
    print(f"Upserted {count} teams from Records API.")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("sync-teams-records", help="Import teams from Records API franchise endpoint")
    p.set_defaults(func=_cmd_sync_teams_records)


