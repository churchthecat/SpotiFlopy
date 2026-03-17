import os
import subprocess
import re
import json

from .library import get_track_path


def clean_title(title: str) -> str:
    patterns = [
        r"\(.*?\)",
        r"- remaster.*",
    ]

    cleaned = title
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", cleaned).strip()


def is_bad_title(title: str) -> bool:
    bad_words = ["live", "cover", "karaoke", "remix"]

    t = title.lower()
    return any(w in t for w in bad_words)


def pick_best_video(results, target_duration):
    best = None
    best_diff = 999

    for r in results:
        title = r.get("title", "")
        duration = r.get("duration")

        if not duration:
            continue

        if is_bad_title(title):
            continue

        diff = abs(duration - target_duration)

        if diff < best_diff:
            best = r
            best_diff = diff

    return best


def search_youtube(query):
    cmd = [
        "yt-dlp",
        f"ytsearch5:{query}",
        "--dump-json",
        "--no-download",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    videos = []
    for line in result.stdout.splitlines():
        try:
            videos.append(json.loads(line))
        except:
            pass

    return videos


def download(track, base_dir):
    artist = track["artist"]
    album = track["album"]
    title = clean_title(track["title"])
    track_number = track["track_number"]
    duration = track.get("duration", 0)

    output_path = get_track_path(base_dir, artist, album, track_number, title)

    if os.path.exists(output_path):
        print(f"Already exists: {output_path}")
        return

    query = f"{artist} - {title} audio"

    print(f"\n=== Searching ===")
    print(f"Query: {query}")

    results = search_youtube(query)

    if not results:
        print("❌ No results")
        return

    best = pick_best_video(results, duration)

    if not best:
        print("❌ No suitable match")
        return

    url = best["webpage_url"]

    print(f"✅ Selected: {best['title']} ({best.get('duration')}s)")

    temp_output = output_path.replace(".mp3", ".%(ext)s")

    cmd = [
        "yt-dlp",
        url,
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", temp_output,
        "--no-playlist",
        "--embed-metadata",
        "--embed-thumbnail",
    ]

    subprocess.run(cmd)

    if os.path.exists(output_path):
        print(f"✅ Saved: {output_path}")
    else:
        print(f"⚠️ Failed: {output_path}")
