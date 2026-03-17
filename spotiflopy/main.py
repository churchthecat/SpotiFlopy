import argparse
import os

from .spotify import get_liked_tracks, get_playlists, get_playlist_tracks
from .downloader import download, build_path
from .state import load_state, save_state, make_key, now_iso


def ensure_symlink(track, base_dir, playlist_dir):
    target = build_path(track, base_dir)

    if not os.path.exists(target):
        return

    os.makedirs(playlist_dir, exist_ok=True)

    link_name = os.path.join(playlist_dir, os.path.basename(target))

    if not os.path.exists(link_name):
        os.symlink(target, link_name)


def sync(state, base_dir, playlists=False, limit=None):
    completed = set(state["completed"])

    tracks = get_liked_tracks()

    if limit:
        tracks = tracks[:limit]

    for t in tracks:
        key = make_key(t)

        if key in completed:
            continue

        if download(t, base_dir):
            completed.add(key)

    if playlists:
        for p in get_playlists():
            print(f"\n🔍 Playlist: {p['name']}")

            playlist_dir = os.path.join(base_dir, "Playlists", p["name"])

            for t in get_playlist_tracks(p["id"]):
                ensure_symlink(t, base_dir, playlist_dir)

    state["completed"] = list(completed)
    state["last_sync"]["all"] = now_iso()
    save_state(state)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["sync", "repair"])
    parser.add_argument("--playlists", action="store_true")
    parser.add_argument("--limit", type=int)

    args = parser.parse_args()

    state = load_state()
    base_dir = os.path.expanduser("~/Music")

    if args.command == "sync":
        sync(state, base_dir, args.playlists, args.limit)


if __name__ == "__main__":
    main()
