import os
import subprocess

OUTPUT_DIR = os.path.expanduser("~/Music")


def download_audio(url, track):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    safe_artist = track.get("artist", "unknown").replace("/", "_")
    safe_title = track.get("title", "unknown").replace("/", "_")

    filename = f"{safe_artist} - {safe_title}.mp3"
    output_path = os.path.join(OUTPUT_DIR, filename)

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_path,
        "--cookies-from-browser", "chromium",
        url
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[SAVED] {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[DOWNLOAD ERROR] {e}")
        return None


import os
import sqlite3
import subprocess
import tempfile
import json

from .tagger import tag_file, embed_cover
from .spotify import get_liked_tracks
from .verification import verify_audio

THRESHOLD = 0.6

DB_PATH = ".spotiflopy.db"
MUSIC_DIR = os.path.expanduser("~/Music")

_db_conn = None


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(tracks)")
    cols = [r[1] for r in cur.fetchall()]

    def add(name, typ):
        if name not in cols:
            cur.execute(f"ALTER TABLE tracks ADD COLUMN {name} {typ}")

    add("youtube_url", "TEXT")

    return conn



# -----------------------------
# SEARCH
# -----------------------------
def search_youtube(query):
    import subprocess
    import json

    cmd = [
        "yt-dlp",
        f"ytsearch5:{query}",
        "--dump-json",
        "--no-playlist",
        "--cookies-from-browser", "chromium",
        "--extractor-args", "youtube:player_client=android",
        "--user-agent", "Mozilla/5.0"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print("[YT ERROR]", result.stderr.strip())
            return []

        lines = result.stdout.strip().split("\n")

        results = []
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                results.append({
                    "title": data.get("title", ""),
                    "url": data.get("webpage_url"),
                    "duration": data.get("duration")
                })
            except Exception:
                continue

        return results

    except Exception as e:
        print(f"[YT EXCEPTION] {e}")
        return []


def score_candidate(track, video):
    score = 0

    title = video["title"].lower()
    artist = track["artist"].lower()
    name = track["title"].lower()

    if artist.split(",")[0] in title:
        score += 2

    if name[:8] in title:
        score += 2

    expected = track.get("duration_ms")
    if expected and video.get("duration"):
        diff = abs(video["duration"] - (expected / 1000))
        if diff < 5:
            score += 3
        elif diff < 10:
            score += 1

    return score


# -----------------------------
# DOWNLOAD HELPER
# -----------------------------
def download_candidate(url, temp_path):
    cmd = [
        "yt-dlp",
        url,
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", temp_path,
        "--quiet",
        "--no-playlist"
    ]

    try:
        subprocess.run(cmd, timeout=120)
        return os.path.exists(temp_path)
    except:
        return False


# -----------------------------
# MAIN DOWNLOAD
# -----------------------------
def download(track):
    query = f"{track['artist']} - {track['title']}"
    print(f"[SEARCH] {query}")

    results = search_youtube(query)

    print(f"[RESULTS] {len(results)} found")

    if not results:
        print("[FAIL] no search results")
        return None, None

    for r in results:
        print(f"[CANDIDATE] {r.get('title')}")

        score = verify_audio(track, r)
        print(f"[VERIFY] {score:.2f}")

        if score >= THRESHOLD:
            print(f"[DOWNLOAD] {r.get('url')}")

            return download_audio(r.get("url"), track)

    print("[FAIL] no candidate passed verification")
    return None, None


def sync_tracks(limit=None):
    from .spotify import get_liked_tracks

    tracks = get_liked_tracks(limit=limit)

    print(f"🎧 Syncing {len(tracks)} tracks")

    for track in tracks:
        result = download(track)

        if result == (None, None):
            print(f"[SKIP] {track['title']}")
        else:
            print(f"[OK] {track['title']}")

    print("✅ Sync complete")


def repair_library(workers=1):
    import os

    print(f"🔧 Repairing library with {workers} workers...")

    from spotiflopy.spotify import get_liked_tracks
    tracks = get_liked_tracks(limit=None)  # your existing function

    for track in tracks:
        artist = track.get("artist")
        title = track.get("title")

        # skip broken data
        if not artist or not title:
            print("[SKIP] invalid track")
            continue

        filename = f"{artist} - {title}.mp3"
        path = os.path.expanduser(f"~/Music/{filename}")

        if not os.path.exists(path):
            print(f"[REPAIR] {artist} - {title}")
            download(track)
        else:
            print(f"[OK] {title}")

    print("✅ Repair done")

