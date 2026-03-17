#!/usr/bin/env bash
set -e

# ---------------- UPGRADE LOGIC ----------------
cat <<'PY' > spotiflopy/upgrade.py
import os


def find_existing_versions(folder, title):
    mp3 = None
    flac = None

    for f in os.listdir(folder):
        if title in f:
            if f.endswith(".mp3"):
                mp3 = os.path.join(folder, f)
            elif f.endswith(".flac"):
                flac = os.path.join(folder, f)

    return mp3, flac


def should_upgrade(mp3, flac, target_format):
    if target_format != "flac":
        return False

    if flac:
        return False  # already best

    if mp3:
        return True

    return False


def replace_file(old_path, new_path):
    try:
        os.remove(old_path)
    except Exception:
        pass
PY

# ---------------- DOWNLOADER PATCH ----------------
cat <<'PY' > spotiflopy/downloader.py
import os
import subprocess
from .tagger import tag_file, embed_cover
from .musicbrainz import enrich_metadata
from .config import load_config
from .upgrade import find_existing_versions, should_upgrade, replace_file


def download(track, base_dir):
    cfg = load_config()

    fmt = cfg.get("audio_format", "mp3")
    quality = cfg.get("audio_quality", "320")

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

    mp3_path, flac_path = find_existing_versions(folder, safe_title)

    # --- upgrade decision ---
    if should_upgrade(mp3_path, flac_path, fmt):
        print(f"⬆️ Upgrading to FLAC: {artist} - {title}")
    else:
        if flac_path or mp3_path:
            return flac_path or mp3_path

    ext = "flac" if fmt == "flac" else "mp3"
    filename = f"{track_num:02d} - {safe_title}.{ext}"
    path = os.path.join(folder, filename)

    query = f"{artist} - {title}"

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--no-playlist",
        "--quiet"
    ]

    if fmt == "flac":
        cmd += ["--extract-audio", "--audio-format", "flac"]
    else:
        cmd += [
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", quality
        ]

    cmd += [
        "-o", path,
        "--embed-metadata",
        "--embed-thumbnail"
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0 or not os.path.exists(path):
        print(f"⚠️ Download failed: {query}")
        return None

    # tagging
    try:
        tag_file(path, track)
    except:
        pass

    if track.get("cover_url"):
        try:
            embed_cover(path, track["cover_url"])
        except:
            pass

    # --- replace old version ---
    if mp3_path and fmt == "flac":
        print(f"🗑 Removing old MP3")
        replace_file(mp3_path, path)

    return path
PY

pip install -e .

echo "Smart upgrade system installed."
