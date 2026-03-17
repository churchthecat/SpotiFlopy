import os
import subprocess
import re

from .library import get_track_path


def clean_title(title: str) -> str:
    patterns = [
        r"\(.*?remaster.*?\)",
        r"\(.*?live.*?\)",
        r"\(.*?version.*?\)",
        r"\(.*?\)",
        r"- remaster.*",
    ]

    cleaned = title
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", cleaned).strip()


def download(track, base_dir):
    artist = track["artist"]
    album = track["album"]
    title = clean_title(track["title"])
    track_number = track["track_number"]

    output_path = get_track_path(base_dir, artist, album, track_number, title)

    if os.path.exists(output_path):
        print(f"Already exists: {output_path}")
        return

    query = f"{artist} - {title}"

    print(f"\n=== Downloading ===")
    print(f"Query: {query}")

    temp_output = output_path.replace(".mp3", ".%(ext)s")

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", temp_output,
        "--no-playlist",
        "--embed-metadata",
        "--embed-thumbnail",
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"❌ yt-dlp failed for: {query}")
        return

    if not os.path.exists(output_path):
        print(f"⚠️ File not found after download: {output_path}")
    else:
        print(f"✅ Saved: {output_path}")
