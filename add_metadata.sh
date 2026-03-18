#!/usr/bin/env bash
set -e

pip install mutagen

# ---------------- TAGGER ----------------
cat <<'PY' > spotiflopy/tagger.py
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests
import os


def tag_file(path, track):
    try:
        audio = EasyID3(path)
    except:
        audio = EasyID3()
        audio.save(path)
        audio = EasyID3(path)

    audio["title"] = track["title"]
    audio["artist"] = track["artist"]

    if track.get("album"):
        audio["album"] = track["album"]

    if track.get("track_number"):
        audio["tracknumber"] = str(track["track_number"])

    audio.save()


def embed_cover(path, url):
    try:
        data = requests.get(url, timeout=10).content

        audio = ID3(path)
        audio["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=data
        )
        audio.save()

    except Exception:
        pass
PY

# ---------------- DOWNLOADER UPDATE ----------------
cat <<'PY' > spotiflopy/downloader.py
import os
import subprocess
from .tagger import tag_file, embed_cover


def download(track, base_dir):
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

    # --- enforce clean tags ---
    tag_file(path, track)

    if track.get("cover_url"):
        embed_cover(path, track["cover_url"])

    return path
PY

pip install -e .

echo "Metadata system installed."
