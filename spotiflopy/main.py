import argparse
import json
from pathlib import Path
from .spotify import get_liked_tracks
from .downloader import download

CONFIG_FILE = Path.cwd() / "config.json"


def init():
    print("=== SpotiFlopy Setup ===\n")

    client_id = input("Spotify Client ID: ").strip()
    client_secret = input("Spotify Client Secret: ").strip()

    default_music_display = "~/Music/SpotiFlopy"
    music_dir = input(f"Music directory [{default_music_display}]: ").strip()

    if not music_dir:
        music_dir = default_music_display

    # normalize but KEEP ~ in config (important)
    music_dir = music_dir.replace(str(Path.home()), "~")

    backend = input("Download backend (yt-dlp) [yt-dlp]: ").strip()
    if not backend:
        backend = "yt-dlp"

    cookies = input("Use browser cookies? (chromium/firefox/none) [chromium]: ").strip()
    if not cookies:
        cookies = "chromium"

    cookies_file = input("Cookies.txt path (optional): ").strip()
    proxy = input("Proxy (optional, e.g. http://127.0.0.1:8080): ").strip()

    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "music_dir": music_dir,
        "backend": backend,
        "cookies_from_browser": cookies,
        "cookies_file": cookies_file,
        "proxy": proxy
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Config saved to {CONFIG_FILE}")


def sync():
    tracks = get_liked_tracks()
    for track in tracks:
        download(track)


def main():
    parser = argparse.ArgumentParser(
        prog="spotiflopy",
        description="Mirror your Spotify liked songs locally"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Setup configuration")
    subparsers.add_parser("sync", help="Download liked songs")

    args = parser.parse_args()

    if args.command == "init":
        init()
    elif args.command == "sync":
        sync()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
