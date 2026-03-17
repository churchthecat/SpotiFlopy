import os
import subprocess
import re
import json
from difflib import SequenceMatcher

from .library import get_track_path

CACHE_FILE = os.path.expanduser("~/.cache/spotiflopy_cache.json")


# ------------------------
# Utils
# ------------------------

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def clean_title(title: str) -> str:
    patterns = [
        r"\(.*?\)",
        r"- remaster.*",
    ]

    for p in patterns:
        title = re.sub(p, "", title, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", title).strip()


def is_bad_title(title: str) -> bool:
    bad_words = ["live", "cover", "karaoke", "remix"]

    t = title.lower()
    return any(w in t for w in bad_words)


def is_good_channel(channel: str) -> bool:
    if not channel:
        return False

    good = ["vevo", "official", "topic"]

    c = channel.lower()
    return any(g in c for g in good)


# ------------------------
# Cache
# ------------------------

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# ------------------------
# Search
# ------------------------

def search_youtube(query):
    cmd = [
        "yt-dlp",
        f"ytsearch7:{query}",
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


# ------------------------
# Scoring
# ------------------------

def score_video(video, artist, title, target_duration):
    vtitle = video.get("title", "")
    duration = video.get("duration") or 0
    channel = video.get("channel", "")

    if is_bad_title(vtitle):
        return -1

    # similarity
    sim = similarity(f"{artist} {title}", vtitle)

    # duration penalty
    diff = abs(duration - target_duration)
    duration_score = max(0, 1 - (diff / 10))  # 10s tolerance

    # channel bonus
    channel_score = 0.2 if is_good_channel(channel) else 0

    return sim + duration_score + channel_score


def pick_best(video_list, artist, title, duration):
    best = None
    best_score = -1

    for v in video_list:
        s = score_video(v, artist, title, duration)

        if s > best_score:
            best = v
            best_score = s

    return best


# ------------------------
# Download
# ------------------------

def download(track, base_dir):
    artist = track["artist"]
    album = track["album"]
    title = clean_title(track["title"])
    track_number = track["track_number"]
    duration = track.get("duration", 0)

    output_path = get_track_path(base_dir, artist, album, track_number, title)

    if os.path.exists(output_path):
        print(f"Already exists: {output_path}")
        return True

    cache = load_cache()
    cache_key = f"{artist}::{title}"

    if cache_key in cache:
        url = cache[cache_key]
        print(f"⚡ Using cached match: {url}")
    else:
        query = f"{artist} - {title} audio"
        print(f"\n=== Searching === {query}")

        results = search_youtube(query)
        if not results:
            print("❌ No results")
            return False

        best = pick_best(results, artist, title, duration)
        if not best:
            print("❌ No suitable match")
            return False

        url = best["webpage_url"]
        cache[cache_key] = url
        save_cache(cache)

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
        "--retries", "3",
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"❌ Download failed: {artist} - {title}")
        return False

    if os.path.exists(output_path):
        print(f"✅ Saved: {output_path}")
        return True
    else:
        print(f"⚠️ Missing file: {output_path}")
        return False
