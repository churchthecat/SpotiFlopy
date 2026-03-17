#!/usr/bin/env bash
set -e

echo "== Resetting core files =="

# ---------------- MAIN ----------------
cat <<'PY' > spotiflopy/main.py
import argparse
import os

from .spotify import get_liked_tracks, get_playlists, get_playlist_tracks
from .downloader import download
from .config import get_music_dir
from .library import repair_library
from .state import load_state, save_state, make_key, now_iso
from .playlist import create_symlink
from .matcher import build_index, find_in_index


def sync_liked(state, completed, base_dir, limit=None):
    since = state.get("last_sync", {}).get("liked")
    tracks = get_liked_tracks(since=since)

    tracks = [t for t in tracks if make_key(t) not in completed]
    if limit:
        tracks = tracks[:limit]

    print(f"\n🎧 Liked Songs: {len(tracks)} new")

    for t in tracks:
        path = download(t, base_dir)
        if path:
            completed.add(make_key(t))

    state.setdefault("last_sync", {})["liked"] = now_iso()
    state["completed"] = list(completed)
    save_state(state)


def sync_playlists(state, completed, base_dir, limit=None):
    playlists = get_playlists()

    print("\n⚡ Building fast index...")
    index = build_index(base_dir)

    for p in playlists:
        key = f"playlist:{p['name']}"
        since = state.get("last_sync", {}).get(key)

        print(f"\n🔍 {p['name']}")

        try:
            tracks = get_playlist_tracks(p["id"], since=since)
        except Exception as e:
            print(f"⚠️ Skipped: {e}")
            continue

        tracks = [t for t in tracks if make_key(t) not in completed]
        if limit:
            tracks = tracks[:limit]

        print(f"📁 {len(tracks)} tracks")

        if not tracks:
            continue

        playlist_dir = os.path.join(base_dir, "Playlists", p["name"])
        os.makedirs(playlist_dir, exist_ok=True)

        for t in tracks:
            path = find_in_index(index, t)

            if path:
                print(f"✅ Found: {t['artist']} - {t['title']}")
            else:
                print(f"⬇️ Download: {t['artist']} - {t['title']}")
                path = download(t, base_dir)

            if not path:
                continue

            dest = os.path.join(playlist_dir, os.path.basename(path))
            create_symlink(path, dest)

            completed.add(make_key(t))

        state.setdefault("last_sync", {})[key] = now_iso()
        state["completed"] = list(completed)
        save_state(state)


def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")
    sub = parser.add_subparsers(dest="cmd")

    s = sub.add_parser("sync")
    s.add_argument("--playlists", action="store_true")
    s.add_argument("--limit", type=int)

    sub.add_parser("repair")

    args = parser.parse_args()

    state = load_state()
    completed = set(state.get("completed", []))
    base_dir = get_music_dir()

    if args.cmd == "sync":
        sync_liked(state, completed, base_dir, args.limit)
        if args.playlists:
            sync_playlists(state, completed, base_dir, args.limit)

    elif args.cmd == "repair":
        repair_library(base_dir)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
PY

# ---------------- MATCHER (FAST INDEX) ----------------
cat <<'PY' > spotiflopy/matcher.py
import os

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum() or c.isspace()).strip()


def build_index(base_dir):
    index = {}

    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.endswith(".mp3"):
                continue

            key = normalize(f)
            index[key] = os.path.join(root, f)

    return index


def find_in_index(index, track):
    query = normalize(f"{track['artist']} {track['title']}")

    # exact-ish lookup
    for k, path in index.items():
        if query in k:
            return path

    return None
PY

# ---------------- PLAYLIST SYMLINK ----------------
cat <<'PY' > spotiflopy/playlist.py
import os

def create_symlink(src, dest):
    try:
        if os.path.exists(dest):
            return
        rel = os.path.relpath(src, os.path.dirname(dest))
        os.symlink(rel, dest)
    except Exception as e:
        print(f"⚠️ Symlink error: {e}")
PY

echo "== Reinstalling =="
pip install -e .

echo "== DONE =="
