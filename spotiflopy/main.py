import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from .spotify import (
    get_liked_tracks,
    get_playlists,
    get_playlist_tracks,
)
from .downloader import download
from .config import get_music_dir
from .library import repair_library
from .state import load_state, save_state, make_key, now_iso
from .init import run_init


def run_downloads(tracks, base_dir, completed, state, workers):
    lock = Lock()
    total = len(tracks)
    done = 0

    def process(track):
        nonlocal done
        path = download(track, base_dir)

        with lock:
            if path:
                completed.add(make_key(track))
                state["completed"] = list(completed)
                save_state(state)

            done += 1
            print(f"[{done}/{total}] {track['artist']} - {track['title']}")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(process, tracks)


def sync_liked(state, completed, workers, base_dir, limit=None):
    since = state["last_sync"].get("liked")
    tracks = get_liked_tracks(since=since)

    tracks = [t for t in tracks if make_key(t) not in completed]

    if limit:
        tracks = tracks[:limit]

    print(f"\n🎧 Liked Songs: {len(tracks)} new")

    run_downloads(tracks, base_dir, completed, state, workers)

    state["last_sync"]["liked"] = now_iso()
    save_state(state)


def sync_playlists(state, completed, workers, base_dir, limit=None):
    playlists = get_playlists()

    for p in playlists:
        key = f"playlist:{p['name']}"
        since = state["last_sync"].get(key)

        print(f"\n🔍 Checking playlist: {p['name']}")

        try:
            tracks = get_playlist_tracks(p["id"], since=since)
        except Exception as e:
            print(f"⚠️ Skipping playlist '{p['name']}': {e}")
            continue

        tracks = [t for t in tracks if make_key(t) not in completed]

        if limit:
            tracks = tracks[:limit]

        print(f"📁 {len(tracks)} new tracks")

        playlist_dir = os.path.join(base_dir, "Playlists", p["name"])
        os.makedirs(playlist_dir, exist_ok=True)

        run_downloads(tracks, playlist_dir, completed, state, workers)

        state["last_sync"][key] = now_iso()
        save_state(state)


def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")
    subparsers = parser.add_subparsers(dest="command")

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--workers", type=int, default=4)
    sync_parser.add_argument("--playlists", action="store_true")
    sync_parser.add_argument("--limit", type=int)

    subparsers.add_parser("repair")
    subparsers.add_parser("init")

    args = parser.parse_args()

    state = load_state()
    completed = set(state["completed"])
    base_dir = get_music_dir()

    if args.command == "sync":
        sync_liked(state, completed, args.workers, base_dir, args.limit)

        if args.playlists:
            sync_playlists(state, completed, args.workers, base_dir, args.limit)

    elif args.command == "repair":
        repair_library(base_dir)

    elif args.command == "init":
        run_init()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
