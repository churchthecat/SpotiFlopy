import os
import sqlite3
import subprocess
import tempfile
import json

from .tagger import tag_file, embed_cover
from .spotify import get_liked_tracks
from .verification import verify_audio

DB_PATH = ".spotiflopy.db"
MUSIC_DIR = os.path.expanduser("~/Music")

_db_conn = None


def get_db():
    global _db_conn

    if _db_conn is None:
        _db_conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
        _db_conn.execute("PRAGMA journal_mode=WAL;")
        _db_conn.execute("PRAGMA synchronous=NORMAL;")

        cur = _db_conn.cursor()
        cur.execute("PRAGMA table_info(tracks)")
        cols = [r[1] for r in cur.fetchall()]

        def add(name, typ):
            if name not in cols:
                cur.execute(f"ALTER TABLE tracks ADD COLUMN {name} {typ}")

        add("youtube_url", "TEXT")

    return _db_conn


# -----------------------------
# SEARCH (FAST + SCORING)
# -----------------------------
def search_youtube(query, max_results=3):
    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--dump-json",
        "--quiet",
        "--no-playlist"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return []

    videos = []
    for line in result.stdout.splitlines():
        try:
            data = json.loads(line)
            title = data.get("title", "").lower()

            # filter garbage early
            if any(x in title for x in ["remix", "live", "cover", "sped", "nightcore"]):
                continue

            videos.append({
                "url": data["webpage_url"],
                "title": data["title"],
                "duration": data.get("duration", 0)
            })
        except:
            continue

    return videos


# -----------------------------
# PRE-SCORE (FAST FILTER)
# -----------------------------
def score_candidate(track, video):
    score = 0

    title = video["title"].lower()
    artist = track["artist"].lower()
    name = track["title"].lower()

    if artist.split(",")[0] in title:
        score += 2

    if name[:8] in title:
        score += 2

    # duration check (fast, before download)
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
def download(track, base_dir=MUSIC_DIR):
    db = get_db()

    artist = track["artist"]
    album = track.get("album") or "Unknown Album"
    title = track["title"]
    track_num = track.get("track_number") or 0

    folder = os.path.join(base_dir, artist, album)
    os.makedirs(folder, exist_ok=True)

    final_path = os.path.join(folder, f"{int(track_num):02d} - {title}.mp3")

    # ✅ instant skip if exists
    if os.path.exists(final_path):
        return final_path, None

    # -----------------------------
    # CACHE
    # -----------------------------
    row = db.execute(
        "SELECT youtube_url FROM tracks WHERE track_id=?",
        (track["id"],)
    ).fetchone()

    if row and row[0]:
        print("[CACHE]")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

        if download_candidate(row[0], tmp):
            score = verify_audio(tmp, track)
            if score >= 0.8:
                os.rename(tmp, final_path)
                tag_file(final_path, track)
                return final_path, row[0]
            else:
                os.remove(tmp)

    # -----------------------------
    # SEARCH + SCORE
    # -----------------------------
    query = f"{artist} - {title}"
    results = search_youtube(query)

    scored = sorted(
        results,
        key=lambda v: score_candidate(track, v),
        reverse=True
    )

    for vid in scored[:2]:  # only try best 2
        print(f"[TRY] {vid['title']}")

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

        if not download_candidate(vid["url"], tmp):
            continue

        score = verify_audio(tmp, track)
        print(f"[VERIFY] {score:.2f}")

        if score >= 0.8:
            os.rename(tmp, final_path)
            tag_file(final_path, track)

            return final_path, vid["url"]

        os.remove(tmp)

    print(f"❌ FAILED: {query}")
    return None, None


# -----------------------------
# SYNC
# -----------------------------
def sync_tracks(limit=None):
    db = get_db()

    tracks = get_liked_tracks(limit=limit)
    print(f"🔄 Syncing {len(tracks)} tracks...")

    for track in tracks:
        path, url = download(track)

        if not path:
            continue

        db.execute("""
            INSERT OR REPLACE INTO tracks
            (track_id, file, artist, title, album, youtube_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track["id"],
            path,
            track["artist"],
            track["title"],
            track.get("album"),
            url
        ))

    print("✅ Done")
