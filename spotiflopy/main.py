import argparse
from spotiflopy.download import sync_tracks, repair_library
from spotiflopy.init import run_init


def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")

    sync_parser = sub.add_parser("sync")
    sync_parser.add_argument("--limit", type=int, default=50)

    sub.add_parser("repair")

    args = parser.parse_args()

    if args.command == "init":
        run_init()
    elif args.command == "sync":
        sync_tracks(limit=args.limit)
    elif args.command == "repair":
        repair_library()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
