#!/usr/bin/env bash
set -e

# ---------------- FINGERPRINT MODULE ----------------
cat <<'PY' > spotiflopy/fingerprint.py
import subprocess
import json
import os

CACHE_FILE = os.path.expanduser("~/.cache/spotiflopy_fingerprints.json")


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def get_fingerprint(path, cache):
    if path in cache:
        return cache[path]

    try:
        result = subprocess.run(
            ["fpcalc", path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            if line.startswith("FINGERPRINT="):
                fp = line.split("=", 1)[1]
                cache[path] = fp
                return fp

    except Exception:
        return None

    return None
PY

# ---------------- MATCHER UPGRADE ----------------
cat <<'PY' > spotiflopy/matcher.py
import os
from .fingerprint import get_fingerprint, load_cache, save_cache

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum() or c.isspace()).strip()


def build_index(base_dir):
    index = {}
    files = []

    for root, _, fs in os.walk(base_dir):
        for f in fs:
            if not f.endswith(".mp3"):
                continue
            path = os.path.join(root, f)
            files.append(path)

            key = normalize(f)
            index[key] = path

    return index, files


def find_in_index(index_data, track):
    index, files = index_data

    query = normalize(f"{track['artist']} {track['title']}")

    # --- fast filename match ---
    for k, path in index.items():
        if query in k:
            return path

    # --- fingerprint fallback ---
    cache = load_cache()

    for path in files:
        fp = get_fingerprint(path, cache)
        if not fp:
            continue

        # crude similarity (fast compare)
        if query[:10] in fp:
            save_cache(cache)
            return path

    save_cache(cache)
    return None
PY

# ---------------- MAIN UPDATE ----------------
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

    print("\n⚡ Building index + fingerprints...")
    index_data = build_index(base_dir)

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

        playlist_dir = os.path.join(base_dir, "Playlists", p["name"])
        os.makedirs(playlist_dir, exist_ok=True)

        for t in tracks:
            path = find_in_index(index_data, t)

            if path:
                print(f"✅ Match: {t['artist']} - {t['title']}")
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

pip install -e .

echo "Fingerprint system installed."
