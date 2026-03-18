import argparse
import json
import os

from spotiflopy.download import sync_tracks, repair_library


CONFIG_PATH = "config.json"


# ----------------------------
# INIT
# ----------------------------
def run_init():
    print("🎧 Spotiflopy setup\n")

    client_id = input("Spotify Client ID: ").strip()
    client_secret = input("Spotify Client Secret: ").strip()
    music_dir = input("Music directory [~/Music]: ").strip() or "~/Music"

    config = {
        "spotify_client_id": client_id,
        "spotify_client_secret": client_secret,
        "music_dir": music_dir
    }

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print("\n✅ Config saved to config.json")
    print("👉 You can now run: spotiflopy sync")


# ----------------------------
# SYNC
# ----------------------------
def run_sync(args):
    sync_tracks(limit=args.limit)


# ----------------------------
# REPAIR
# ----------------------------
def run_repair(args):
    repair_library(
        workers=args.workers,
        full=args.full,
        fs=args.fs
    )


# ----------------------------
# MAIN
# ----------------------------
def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")

    subparsers = parser.add_subparsers(dest="command")

    # INIT
    subparsers.add_parser("init")

    # SYNC
    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--limit", type=int)

    # REPAIR
    repair_parser = subparsers.add_parser("repair")
    repair_parser.add_argument("--workers", type=int, default=1)
    repair_parser.add_argument("--full", action="store_true", help="Fetch ALL Spotify tracks")
    repair_parser.add_argument("--fs", action="store_true", help="Filesystem scan only")

    args = parser.parse_args()

    if args.command == "init":
        run_init()
    elif args.command == "sync":
        run_sync(args)
    elif args.command == "repair":
        run_repair(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
