import argparse
from .spotify import get_liked_tracks
from .downloader import download
from .config import get_music_dir
from .library import repair_library


def sync(limit=None):
    tracks = get_liked_tracks()

    if limit:
        tracks = tracks[:limit]

    music_dir = get_music_dir()

    for t in tracks:
        download(t, music_dir)


def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")

    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init")

    # sync
    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of tracks (for testing)"
    )

    # repair
    repair_parser = subparsers.add_parser("repair")

    args = parser.parse_args()

    if args.command == "sync":
        sync(limit=args.limit)

    elif args.command == "repair":
        repair_library(get_music_dir())

    elif args.command == "init":
        print("Run setup via config files (init placeholder)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
