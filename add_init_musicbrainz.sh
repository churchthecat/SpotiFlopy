#!/usr/bin/env bash
set -e

pip install musicbrainzngs

# ---------------- CONFIG ----------------
cat <<'PY' > spotiflopy/config.py
import os
import json

CONFIG_PATH = os.path.expanduser("~/.spotiflopy.json")


DEFAULT_CONFIG = {
    "client_id": "",
    "client_secret": "",
    "redirect_uri": "http://127.0.0.1:8888/callback",
    "music_dir": "~/Music",
    "backend": "yt-dlp",
    "cookies_from_browser": "chromium",
    "cookies_file": "",
    "proxy": "",
    "acoustid_key": ""
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)

    # merge defaults (important for upgrades)
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get_music_dir():
    return os.path.expanduser(load_config()["music_dir"])
PY

# ---------------- INIT COMMAND ----------------
cat <<'PY' > spotiflopy/init.py
from .config import load_config, save_config


def run_init():
    cfg = load_config()

    print("🎧 SpotiFlopy Setup\n")

    def ask(key, label, default=None, secret=False):
        current = cfg.get(key, "")
        prompt = f"{label}"
        if current:
            prompt += f" [{current}]"
        if default:
            prompt += f" (default: {default})"
        prompt += ": "

        val = input(prompt).strip()
        if val:
            return val
        if current:
            return current
        return default or ""

    cfg["client_id"] = ask("client_id", "Spotify Client ID")
    cfg["client_secret"] = ask("client_secret", "Spotify Client Secret")
    cfg["redirect_uri"] = ask(
        "redirect_uri",
        "Redirect URI",
        "http://127.0.0.1:8888/callback"
    )

    cfg["music_dir"] = ask("music_dir", "Music directory", "~/Music")

    print("\n(Optional) Better matching:")
    print("👉 Get key at https://acoustid.org/api-key")

    cfg["acoustid_key"] = ask(
        "acoustid_key",
        "AcoustID API Key (optional)"
    )

    save_config(cfg)

    print("\n✅ Config saved to ~/.spotiflopy.json")
PY

# ---------------- MUSICBRAINZ ----------------
cat <<'PY' > spotiflopy/musicbrainz.py
import musicbrainzngs

musicbrainzngs.set_useragent("spotiflopy", "1.0", "https://github.com")


def enrich_metadata(artist, title):
    try:
        result = musicbrainzngs.search_recordings(
            recording=title,
            artist=artist,
            limit=1
        )

        recs = result.get("recording-list", [])
        if not recs:
            return None

        r = recs[0]

        return {
            "title": r.get("title"),
            "artist": r["artist-credit"][0]["artist"]["name"],
            "album": r.get("release-list", [{}])[0].get("title"),
            "year": r.get("first-release-date", "")[:4],
        }

    except Exception:
        return None
PY

# ---------------- DOWNLOADER UPDATE ----------------
cat <<'PY' > spotiflopy/downloader.py
import os
import subprocess
from .tagger import tag_file, embed_cover
from .musicbrainz import enrich_metadata


def download(track, base_dir):
    # --- enrich metadata ---
    enriched = enrich_metadata(track["artist"], track["title"])
    if enriched:
        track.update({k: v for k, v in enriched.items() if v})

    artist = track["artist"]
    album = track.get("album") or "Unknown Album"
    title = track["title"]
    track_num = track.get("track_number", 0)

    safe_artist = artist.replace("/", "-")
    safe_album = album.replace("/", "-")
    safe_title = title.replace("/", "-")

    folder = os.path.join(base_dir, safe_artist, safe_album)
    os.makedirs(folder, exist_ok=True)

    filename = f"{track_num:02d} - {safe_title}.mp3"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        return path

    query = f"{artist} - {title}"

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--extract-audio",
        "--audio-format", "mp3",
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails", "png",
        "-o", path,
        "--no-playlist",
        "--quiet"
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0 or not os.path.exists(path):
        print(f"⚠️ Download failed: {query}")
        return None

    tag_file(path, track)

    if track.get("cover_url"):
        embed_cover(path, track["cover_url"])

    return path
PY

# ---------------- MAIN UPDATE ----------------
cat <<'PY' > spotiflopy/main.py
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
PY

pip install -e .

echo "Init + MusicBrainz + config upgrade installed."
