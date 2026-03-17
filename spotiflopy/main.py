import argparse

from spotiflopy.download import sync_tracks, repair_library
from spotiflopy.config import save_config


def run_init():
    print("🎧 SpotiFlopy setup\n")

    client_id = input("Spotify Client ID: ").strip()
    client_secret = input("Spotify Client Secret: ").strip()
    redirect_uri = input("Redirect URI [http://127.0.0.1:8888/callback]: ").strip()

    if not redirect_uri:
        redirect_uri = "http://127.0.0.1:8888/callback"

    cfg = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }

    save_config(cfg)

    print("✅ Config saved to ~/.spotiflopy.json")
    print("👉 Now run: spotiflopy sync")


def run_sync(args):
    sync_tracks(limit=args.limit)


def run_repair(args):
    repair_library(workers=args.workers)


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="cmd")

    # init
    sub.add_parser("init")

    # sync
    s = sub.add_parser("sync")
    s.add_argument("--limit", type=int, default=None)

    # repair
    r = sub.add_parser("repair")
    r.add_argument("--workers", type=int, default=1)

    args = parser.parse_args()

    if args.cmd == "init":
        run_init()
    elif args.cmd == "sync":
        run_sync(args)
    elif args.cmd == "repair":
        run_repair(args)
    else:
        parser.print_help()
