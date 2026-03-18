import os
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor

DB_PATH = ".spotiflopy.db"


def get_db():
    return sqlite3.connect(DB_PATH)


# -----------------------------
# Fingerprint
# -----------------------------
def fingerprint_file(path):
    try:
        result = subprocess.run(
            ["fpcalc", "-json", path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return None

        import json
        data = json.loads(result.stdout)
        return data.get("fingerprint")
    except Exception:
        return None


# -----------------------------
# Scoring
# -----------------------------
def score_result(query, title):
    query = query.lower()
    title = title.lower()

    score = 0

    for word in query.split():
        if word in title:
            score += 2

    if title.startswith(query[:10]):
        score += 5

    return score


# -----------------------------
# Smart YouTube search
# -----------------------------
def search_youtube(query):
    import json

    try:
        result = subprocess.run(
            ["yt-dlp", "ytsearch5:" + query, "--dump-json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        lines = result.stdout.strip().split("\n")

        best_url = None
        best_score = 0

        for line in lines:
            try:
                data = json.loads(line)
            except Exception:
                continue

            title = data.get("title", "")
            vid = data.get("id")

            if not vid:
                continue

            score = score_result(query, title)

            if score > best_score:
                best_score = score
                best_url = f"https://www.youtube.com/watch?v={vid}"

        # avoid garbage matches
        if best_score < 3:
            return None

        return best_url

    except Exception:
        return None


# -----------------------------
# Repair Logic
# -----------------------------
def repair_track(row):
    track_id, file_path, url, fingerprint, _ = row

    if not file_path or not os.path.exists(file_path):
        return

    conn = get_db()
    cur = conn.cursor()

    # Fingerprint
    if not fingerprint:
        fp = fingerprint_file(file_path)
        if fp:
            cur.execute(
                "UPDATE tracks SET fingerprint=? WHERE track_id=?",
                (fp, track_id)
            )
            print(f"[FP] {file_path}")

    # URL recovery
    if not url:
        name = os.path.basename(file_path)
        query = name.replace(".mp3", "").replace(".flac", "")

        yt = search_youtube(query)

        if yt:
            cur.execute(
                "UPDATE tracks SET url=? WHERE track_id=?",
                (yt, track_id)
            )
            print(f"[URL] {query} -> {yt}")

    conn.commit()
    conn.close()


def repair_library(workers=4):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tracks")
    rows = cur.fetchall()
    conn.close()

    print(f"🔧 Repairing {len(rows)} tracks...")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        ex.map(repair_track, rows)

    print("✅ Repair complete")


# -----------------------------
# Sync (placeholder for now)
# -----------------------------
def sync_tracks(tracks, workers=4):
    print(f"🎧 Syncing {len(tracks)} tracks...")
    print("✅ Sync done")
