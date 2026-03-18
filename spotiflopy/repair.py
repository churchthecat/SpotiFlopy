import os
import re
import yt_dlp

from spotiflopy.spotify import get_tracks
from spotiflopy.youtube import search_youtube
from spotiflopy.state import get_track, upsert_track, cleanup_missing_files
from spotiflopy.verification import verify as acoustid_verify
from spotiflopy.tagger import tag_file
from spotiflopy.config import load_config


def safe(s):
    return re.sub(r'[\\/:"*?<>|]+', '', (s or "")).strip()


def build_path(track, music_dir):
    artist = safe(track.get("artist"))
    album = safe(track.get("album"))
    title = safe(track.get("title"))
    num = str(track.get("track_number", 0)).zfill(2)

    return os.path.join(
        music_dir,
        artist,
        album,
        f"{num} - {title}.mp3"
    )


def download_audio(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": path.replace(".mp3", ".%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return path


def download_track(track):
    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    track_id = track.get("spotify_id")
    db_entry = get_track(track_id)

    if db_entry and db_entry.get("status") == "ok":
        if db_entry.get("file") and os.path.exists(db_entry.get("file")):
            print(f"[SKIP] {track['title']}")
            return

    query = f"{track['artist']} - {track['title']}"
    print(f"[SEARCH] {query}")

    results = search_youtube(query)

    for i, r in enumerate(results[:3], 1):
        url = r.get("url")
        title = r.get("title")

        print(f"[TRY {i}/3] {title}")

        path = build_path(track, music_dir)

        try:
            saved = download_audio(url, path)

            print("[VERIFY]")
            ok, fingerprint = acoustid_verify(track, saved)

            if ok is False:
                print("[REJECT]")
                os.remove(saved)
                continue

            tag_file(saved, track)

            upsert_track(
                track_id,
                file=saved,
                url=url,
                fingerprint=fingerprint,
                status="ok"
            )

            print("[SUCCESS]")
            return

        except Exception as e:
            print("[ERROR]", e)

    print("[FAIL]")
    upsert_track(track_id, status="failed")


def repair_library(full=False):
    cleanup_missing_files()

    tracks = get_tracks(all_tracks=full)

    print(f"🔧 Repairing {len(tracks)} tracks...")

    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    for track in tracks:
        expected = build_path(track, music_dir)

        if os.path.exists(expected):
            print(f"[TAG FIX] {track['title']}")
            tag_file(expected, track)
            upsert_track(track["spotify_id"], file=expected, status="ok")
        else:
            print(f"[REPAIR] {track['artist']} - {track['title']}")
            download_track(track)

    print("✅ Repair complete")
