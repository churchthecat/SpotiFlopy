import os
import re
import yt_dlp

from spotiflopy.youtube import search_youtube
from spotiflopy.verification import verify_match
from spotiflopy.spotify import get_tracks
from spotiflopy.config import load_config
from spotiflopy.db import get_track, upsert_track


# ----------------------------
# HELPERS
# ----------------------------
def safe(s):
    return re.sub(r'[\\/:"*?<>|]+', '', (s or "")).strip()


def build_output_template(track, music_dir):
    artist = safe(track.get("artist", "Unknown"))
    album = safe(track.get("album", "Unknown"))
    title = safe(track.get("title", "Unknown"))
    track_num = str(track.get("track_number", 0)).zfill(2)

    return os.path.join(
        music_dir,
        artist,
        album,
        f"{track_num} - {title}.%(ext)s"
    )


# ----------------------------
# DOWNLOAD AUDIO
# ----------------------------
def download_audio(url, track, music_dir):
    outtmpl = build_output_template(track, music_dir)

    os.makedirs(os.path.dirname(outtmpl), exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return outtmpl.replace("%(ext)s", "mp3")


# ----------------------------
# NORMALIZE RESULT
# ----------------------------
def normalize_result(r):
    if isinstance(r, dict):
        return r.get("title", ""), r.get("url", "")
    return r, r


# ----------------------------
# CORE LOGIC
# ----------------------------
def try_download(url, track, music_dir):
    try:
        path = download_audio(url, track, music_dir)
        print(f"[SAVED] {path}")

        upsert_track(
            track.get("spotify_id"),
            file=path,
            url=url
        )
        return True

    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        return False


# ----------------------------
# DOWNLOAD TRACK
# ----------------------------
def download(track):
    track_id = track.get("spotify_id")

    db_entry = get_track(track_id)

    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    # ✅ 1. SKIP if already downloaded
    if db_entry and db_entry.get("file") and os.path.exists(db_entry["file"]):
        print(f"[SKIP] Already downloaded: {track.get('title')}")
        return

    # ✅ 2. TRY REUSE CACHED URL
    if db_entry and db_entry.get("url"):
        print(f"[REUSE] Cached URL")

        success = try_download(db_entry["url"], track, music_dir)

        if success:
            return
        else:
            print("[FALLBACK] Cached URL failed, re-searching...")

    # ----------------------------
    # SEARCH FLOW
    # ----------------------------
    query = f"{track.get('artist')} - {track.get('title')}"
    print(f"[SEARCH] {query}")

    results = search_youtube(query)
    print(f"[RESULTS] {len(results)} found")

    best = None
    best_score = 0

    for r in results:
        title, url = normalize_result(r)
        score = verify_match(track, title)

        if score > best_score:
            best = (title, url)
            best_score = score

    print(f"[VERIFY] {best_score:.2f}")

    if not best:
        print("[FAIL] No match")
        upsert_track(track_id, fingerprint=0)
        return

    if best_score < 0.7:
        print("[FAIL] Low confidence")
        upsert_track(track_id, fingerprint=best_score)
        return

    _, url = best

    print(f"[DOWNLOAD] {url}")

    success = try_download(url, track, music_dir)

    if success:
        upsert_track(
            track_id,
            url=url,
            fingerprint=best_score
        )
    else:
        upsert_track(track_id, fingerprint=best_score)


# ----------------------------
# SYNC
# ----------------------------
def sync_tracks(limit=None):
    tracks = get_tracks(all_tracks=False)

    if limit:
        tracks = tracks[:limit]

    print(f"🎧 Syncing {len(tracks)} tracks")

    for track in tracks:
        download(track)

    print("✅ Sync complete")


# ----------------------------
# REPAIR
# ----------------------------
def repair_library(workers=1, full=False, fs=False):
    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    if fs:
        print("🔍 Filesystem scan mode")

        for root, _, files in os.walk(music_dir):
            for f in files:
                path = os.path.join(root, f)

                if f.endswith(".part") or ".tmp" in f:
                    print(f"[CLEAN] {path}")
                    try:
                        os.remove(path)
                    except Exception as e:
                        print("[ERROR]", e)

        print("✅ Filesystem scan done")
        return

    tracks = get_tracks(all_tracks=full)

    print(f"🔧 Repairing {len(tracks)} tracks...")

    for track in tracks:
        track_id = track.get("spotify_id")

        expected = build_output_template(track, music_dir).replace("%(ext)s", "mp3")

        if os.path.exists(expected):
            print(f"[OK] {track.get('title')}")
            upsert_track(track_id, file=expected)
            continue

        print(f"[REPAIR] {track.get('artist')} - {track.get('title')}")
        download(track)

    print("✅ Repair done")
