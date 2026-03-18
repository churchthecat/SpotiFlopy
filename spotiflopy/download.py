import os
import re
import yt_dlp

from spotiflopy.youtube import search_youtube
from spotiflopy.spotify import get_tracks
from spotiflopy.config import load_config
from spotiflopy.db import get_track, upsert_track
from spotiflopy.acoustid_verify import verify as acoustid_verify
from spotiflopy.metadata import tag_file


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


def normalize(text):
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def verify_match(track, result):
    artist = normalize(track.get("artist", ""))
    title = normalize(track.get("title", ""))
    result_title = normalize(result)

    score = 0

    if artist and artist in result_title:
        score += 0.5

    if title and title in result_title:
        score += 0.5

    if result_title.startswith(f"{artist} {title}"):
        score += 0.3

    return min(score, 1.0)


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


def try_download(url, track, music_dir, score=0):
    try:
        path = download_audio(url, track, music_dir)
        print(f"[SAVED] {path}")

        print("[ACOUSTID] Verifying...")
        ok, fingerprint = acoustid_verify(track, path)

        if ok is True:
            print("[OK] Fingerprint match")

        elif ok is None:
            print("[WARN] Verification skipped")
            if score < 0.9:
                print("[REJECT]")
                os.remove(path)
                return False

        else:
            if score < 1.0:
                print("[REJECT] Fingerprint mismatch")
                os.remove(path)
                return False
            print("[WARN] Fingerprint mismatch but PERFECT match → accepting")

        print("[TAG] Writing metadata...")
        tag_file(path, track)

        upsert_track(
            track.get("spotify_id"),
            file=path,
            url=url,
            fingerprint=fingerprint,
            status="ok"
        )

        print("[SUCCESS]")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def download(track, retry_failed=False):
    track_id = track.get("spotify_id")
    db_entry = get_track(track_id)

    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    if db_entry:
        if db_entry.get("status") == "ok" and os.path.exists(db_entry.get("file", "")):
            print(f"[SKIP] {track.get('title')}")
            return

        if db_entry.get("status") == "failed" and not retry_failed:
            print(f"[SKIP FAILED] {track.get('title')}")
            return

    query = f"{track.get('artist')} - {track.get('title')}"
    print(f"[SEARCH] {query}")

    results = search_youtube(query)

    candidates = []
    for r in results:
        title = r.get("title")
        url = r.get("url")
        score = verify_match(track, title)

        if score >= 0.75:
            candidates.append((score, title, url))

    if not candidates:
        print("[FAIL] No high-quality matches")
        upsert_track(track_id, status="failed")
        return

    candidates.sort(reverse=True, key=lambda x: x[0])

    for i, (score, title, url) in enumerate(candidates[:3], 1):
        print(f"[TRY {i}/3] {title} ({score:.2f})")

        if try_download(url, track, music_dir, score):
            return

    print("[FAIL] All attempts failed")
    upsert_track(track_id, status="failed")


def sync_tracks(limit=None):
    tracks = get_tracks(all_tracks=False)

    if limit:
        tracks = tracks[:limit]

    print(f"🎧 Syncing {len(tracks)} tracks")

    for track in tracks:
        download(track)

    print("✅ Sync complete")


def repair_library(workers=1, full=False, fs=False):
    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    tracks = get_tracks(all_tracks=full)

    print(f"🔧 Repairing {len(tracks)} tracks...")

    for track in tracks:
        track_id = track.get("spotify_id")
        db_entry = get_track(track_id)

        expected = build_output_template(track, music_dir).replace("%(ext)s", "mp3")

        if os.path.exists(expected):
            print(f"[TAG FIX] {track.get('title')}")
            tag_file(expected, track)
            upsert_track(track_id, file=expected, status="ok")
            continue

        print(f"[REPAIR] {track.get('artist')} - {track.get('title')}")
        download(track)

    print("✅ Repair done")
