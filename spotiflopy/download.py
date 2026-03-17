import os
import sqlite3
import subprocess
import tempfile

from .tagger import tag_file, embed_cover
from .spotify import get_liked_tracks
from .verification import verify_audio

DB_PATH = ".spotiflopy.db"
MUSIC_DIR = os.path.expanduser("~/Music")

# -----------------------------
# DB (single connection, safe)
# -----------------------------
_db_conn = None

def get_db():
    global _db_conn

    if _db_conn is None:
        _db_conn = sqlite3.connect(
            DB_PATH,
            timeout=30,
            isolation_level=None
        )

        _db_conn.execute("PRAGMA journal_mode=WAL;")
        _db_conn.execute("PRAGMA synchronous=NORMAL;")

        cur = _db_conn.cursor()

        cur.execute("PRAGMA table_info(tracks)")
        columns = [row[1] for row in cur.fetchall()]

        def add_column(name, definition):
            if name not in columns:
                print(f"[DB] Adding column: {name}")
                cur.execute(f"ALTER TABLE tracks ADD COLUMN {name} {definition}")

        add_column("youtube_url", "TEXT")
        add_column("album", "TEXT")
        add_column("track_number", "INTEGER")
        add_column("year", "TEXT")
        add_column("cover_url", "TEXT")

    return _db_conn


# -----------------------------
# SEARCH (filtered)
# -----------------------------
def clean_query(artist, title):
    import re

    # keep only first artist
    artist = artist.split(",")[0]

    # remove (...) and [...]
    title = re.sub(r"\(.*?\)|\[.*?\]", "", title)

    # remove common junk
    junk = [
        "remaster", "remastered", "version",
        "feat.", "ft.", "official", "audio",
        "lyrics", "video"
    ]

    t = title.lower()
    for j in junk:
        t = t.replace(j, "")

    title = t.strip()

    return f"{artist} {title}".strip()


def search_youtube(query, max_results=5):
    import json
    import subprocess

    def run_search(q):
        cmd = [
            "yt-dlp",
            f"ytsearch{max_results}:{q}",
            "--dump-json",
            "--no-playlist",
            "--quiet"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return []

        videos = []

        for line in result.stdout.splitlines():
            try:
                data = json.loads(line)
                videos.append({
                    "url": data.get("webpage_url"),
                    "title": data.get("title")
                })
            except:
                continue

        return videos

    # pass 1: cleaned query
    videos = run_search(query)

    if videos:
        return videos

    # pass 2: aggressive clean
    parts = query.split(" - ")
    if len(parts) == 2:
        clean = clean_query(parts[0], parts[1])
        print(f"[SEARCH FIX] {clean}")
        videos = run_search(clean)
        if videos:
            return videos

    # pass 3: title only
    title_only = query.split(" - ")[-1]
    print(f"[FALLBACK] {title_only}")
    return run_search(title_only)


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

    result = subprocess.run(cmd)
    return result.returncode == 0 and os.path.exists(temp_path)


# -----------------------------
# MAIN DOWNLOAD
# -----------------------------
def download(track, base_dir=MUSIC_DIR):
    artist = track.get("artist")
    album = track.get("album") or "Unknown Album"
    title = track.get("title")
    track_num = track.get("track_number") or 0

    safe_artist = artist.replace("/", "-")
    safe_album = album.replace("/", "-")
    safe_title = title.replace("/", "-")

    folder = os.path.join(base_dir, safe_artist, safe_album)
    os.makedirs(folder, exist_ok=True)

    final_path = os.path.join(
        folder,
        f"{int(track_num):02d} - {safe_title}.mp3"
    )

    if os.path.exists(final_path):
        return final_path, None

    query = f"{artist} - {title}"

    candidates = search_youtube(query, max_results=5)
    print(f"[SEARCH] {query} → {len(candidates)}")

    for i, vid in enumerate(candidates, 1):
        print(f"[TRY {i}] {vid['title']}")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            temp_path = tmp.name

        if not download_candidate(vid["url"], temp_path):
            continue

        score = verify_audio(temp_path, track)
        print(f"[VERIFY] score={score:.2f}")

        if score >= 0.75:
            print("[ACCEPT]")

            os.rename(temp_path, final_path)

            tag_file(final_path, track)
            if track.get("cover_url"):
                embed_cover(final_path, track["cover_url"])

            return final_path, vid["url"]

        os.remove(temp_path)

    print(f"❌ FAILED: {query}")
    return None, None


# -----------------------------
# SYNC (single writer)
# -----------------------------
def sync_tracks(input_tracks=None):
    db = get_db()

    if input_tracks is None:
        tracks = get_liked_tracks()
    elif isinstance(input_tracks, int):
        tracks = get_liked_tracks(limit=input_tracks)
    elif isinstance(input_tracks, list):
        tracks = input_tracks
    else:
        raise ValueError("sync_tracks expects None, int, or list")

    print(f"🔄 Syncing {len(tracks)} tracks...")

    for track in tracks:
        path, youtube_url = download(track)

        if not path:
            continue

        try:
            db.execute("BEGIN IMMEDIATE")

            db.execute("""
                INSERT OR REPLACE INTO tracks
                (track_id, file, artist, title, album, track_number, year, cover_url, youtube_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track.get("id"),
                path,
                track.get("artist"),
                track.get("title"),
                track.get("album"),
                track.get("track_number"),
                track.get("year"),
                track.get("cover_url"),
                youtube_url
            ))

            db.commit()

        except Exception as e:
            db.rollback()
            print("[DB ERROR]", e)

    print("✅ Sync complete")


# -----------------------------
# REPAIR
# -----------------------------
def repair_track(row):
    file_path = row[1]

    if not file_path or not os.path.exists(file_path):
        return

    track = {
        "title": row[7],
        "artist": row[6],
        "album": row[10],
        "track_number": row[11],
        "year": row[12],
        "cover_url": row[13]
    }

    tag_file(file_path, track)

    if track.get("cover_url"):
        embed_cover(file_path, track["cover_url"])

    print(f"[OK] {file_path}")


def repair_library(workers=4):
    db = get_db()
    rows = db.execute("SELECT * FROM tracks").fetchall()

    print(f"🔧 Repairing {len(rows)} tracks...")

    for row in rows:
        repair_track(row)

    print("✅ Repair complete")
