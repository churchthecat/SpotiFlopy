import os
import subprocess
import json


def search_youtube(query):
    try:
        result = subprocess.run(
            ["yt-dlp", f"ytsearch5:{query}", "--dump-json"],
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().split("\n")
        return [json.loads(l) for l in lines if l.strip()]
    except Exception:
        return []


def download_audio(url, output_path):
    subprocess.run([
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", output_path.replace(".mp3", ".%(ext)s"),
        url
    ])
    return output_path


def build_path(track, music_dir):
    artist = track.get("artist", "Unknown")
    album = track.get("album", "Unknown")
    title = track.get("title", "track")

    base = music_dir or os.path.expanduser("~/Music")
    folder = os.path.join(base, artist, album)

    os.makedirs(folder, exist_ok=True)

    return os.path.join(folder, f"{title}.mp3")


def is_likely_correct(track, result):
    title = (result.get("title") or "").lower()
    artist = track.get("artist", "").lower().split(",")[0]
    song = track.get("title", "").lower()

    return artist in title and song in title


def repair_track(track, music_dir=None):
    artist = track.get("artist")
    title = track.get("title")

    print(f"[SEARCH] {artist} - {title}")

    results = search_youtube(f"{artist} {title}")

    if not results:
        print("[FAIL] No results")
        return False

    for i, r in enumerate(results[:3], 1):
        print(f"[TRY {i}/3] {r.get('title')}")

        try:
            path = build_path(track, music_dir)
            download_audio(r["webpage_url"], path)

            if is_likely_correct(track, r):
                print("[OK*] Accepted match")
                return True

        except Exception as e:
            print(f"[ERROR] {e}")
            continue

    # 🔥 FINAL FALLBACK (always download first result)
    try:
        print("[FALLBACK] Using first result anyway")
        path = build_path(track, music_dir)
        download_audio(results[0]["webpage_url"], path)
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


# 🔧 Compatibility wrapper (for old library.py)
def process_track(track, music_dir=None):
    return repair_track(track, music_dir=music_dir)
