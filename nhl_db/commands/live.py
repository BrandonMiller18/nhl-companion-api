import argparse

from ..services.live_service import update_live_once, watch_live_games


def _cmd_update_live(args: argparse.Namespace) -> None:
    game_id = int(args.game)
    count = update_live_once(game_id)
    print(f"Updated game {game_id}; upserted {count} plays.")


def _cmd_watch_live(args: argparse.Namespace) -> None:
    watch_live_games(poll_seconds=int(args.poll_seconds))


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("update-live", help="Update live game state and plays for a gameId")
    p.add_argument("game", help="Game ID (e.g., 2025020001)")
    p.set_defaults(func=_cmd_update_live)

    p2 = subparsers.add_parser("watch-live", help="Continuously watch all LIVE games and update DB")
    p2.add_argument("--poll-seconds", type=int, default=5, help="Polling interval in seconds")
    p2.set_defaults(func=_cmd_watch_live)


