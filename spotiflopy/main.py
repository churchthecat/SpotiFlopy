import argparse
import os
from dotenv import load_dotenv, set_key

# 🔥 LOAD ENV HERE (critical)
load_dotenv()

from .spotify import get_liked_tracks
from .downloader import download


ENV_FILE = ".env"


def run_init():
    print("🔧 SpotiFlopy setup\n")

    client_id = input("Spotify Client ID: ").strip()
    client_secret = input("Spotify Client Secret: ").strip()
    redirect_uri = input(
        "Redirect URI [http://127.0.0.1:8888/callback]: "
    ).strip() or "http://127.0.0.1:8888/callback"

    if not os.path.exists(ENV_FILE):
        open(ENV_FILE, "w").close()

    set_key(ENV_FILE, "SPOTIPY_CLIENT_ID", client_id)
    set_key(ENV_FILE, "SPOTIPY_CLIENT_SECRET", client_secret)
    set_key(ENV_FILE, "SPOTIPY_REDIRECT_URI", redirect_uri)

    print("\n✅ Saved to .env")
    print("👉 Run: spotiflopy sync\n")


def run_sync(args):
    base_dir = os.path.expanduser("~/Music")

    tracks = get_liked_tracks()

    if args.limit:
        tracks = tracks[:args.limit]

    print(f"🎧 Syncing {len(tracks)} tracks...\n")

    for t in tracks:
        ok = download(t, base_dir)

        if ok:
            print(f"✔ {t['artist']} - {t['title']}")
        else:
            print(f"✖ {t['artist']} - {t['title']}")


def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")

    sync = sub.add_parser("sync")
    sync.add_argument("--limit", type=int)

    args = parser.parse_args()

    if args.command == "init":
        run_init()

    elif args.command == "sync":
        run_sync(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
