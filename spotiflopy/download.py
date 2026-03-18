import os
import yt_dlp

from spotiflopy.youtube import search_youtube
from spotiflopy.verification import verify_match
from spotiflopy.spotify import get_tracks
from spotiflopy.config import load_config


# ----------------------------
# PATH BUILDER
# ----------------------------
def build_output_template(track, music_dir):
    artist = track.get("artist", "Unknown").strip()
    album = track.get("album", "Unknown").strip()
    title = track.get("title", "Unknown").strip()
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

    print(f"[DEBUG] outtmpl = {outtmpl}")

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
# DOWNLOAD TRACK
# ----------------------------
def download(track):
    query = f"{track['artist']} - {track['title']}"
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
        print("[SKIP] No match")
        return

    if best_score < 0.7:
        print("[SKIP] Low confidence")
        return

    title, url = best

    print(f"[DOWNLOAD] {url}")

    config = load_config()
    music_dir = os.path.expanduser(config.get("music_dir", "~/Music"))

    path = download_audio(url, track, music_dir)

    print(f"[SAVED] {path}")


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

    # ----------------------------
    # FILESYSTEM MODE
    # ----------------------------
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

    # ----------------------------
    # SPOTIFY MODE
    # ----------------------------
    tracks = get_tracks(all_tracks=full)

    print(f"🔧 Repairing {len(tracks)} tracks...")

    for track in tracks:
        title = track.get("title")

        expected = build_output_template(track, music_dir).replace("%(ext)s", "mp3")

        if os.path.exists(expected):
            print(f"[OK] {title}")
            continue

        print(f"[REPAIR] {track.get('artist')} - {title}")
        download(track)

    print("✅ Repair done")
