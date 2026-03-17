import argparse
from dotenv import load_dotenv

# ✅ CRITICAL: load .env before anything else
load_dotenv()

from spotiflopy.spotify import get_liked_tracks
from spotiflopy.download import repair_library, sync_tracks


def run_sync(args):
    tracks = get_liked_tracks(limit=args.limit)
    sync_tracks(tracks)


def run_repair(args):
    repair_library(workers=args.workers)


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="command")

    # sync
    sync_cmd = sub.add_parser("sync")
    sync_cmd.add_argument("--limit", type=int, default=None)

    # repair
    repair_cmd = sub.add_parser("repair")
    repair_cmd.add_argument("--workers", type=int, default=4)

    args = parser.parse_args()

    if args.command == "sync":
        run_sync(args)
    elif args.command == "repair":
        run_repair(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
