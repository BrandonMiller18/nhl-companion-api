import argparse

from ..services.schedule_service import sync_schedule_dates


def _cmd_sync_schedule_dates(args: argparse.Namespace) -> None:
    total = sync_schedule_dates(args.start, args.end)
    print(f"Finished upserting {total} games across {args.start}..{args.end}.")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("sync-schedule-dates", help="Import schedule by date range (inclusive)")
    p.add_argument("start", help="YYYY-MM-DD")
    p.add_argument("end", help="YYYY-MM-DD")
    p.set_defaults(func=_cmd_sync_schedule_dates)


