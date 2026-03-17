import os
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests

from .fingerprint import load_cache, save_cache, get_fingerprint, is_match

cache = load_cache()


def safe(s):
    return "".join(c for c in s if c not in '/\\?%*:|"<>').strip()


def build_path(track, base_dir):
    artist = safe(track["artist"])
    album = safe(track["album"])
    title = safe(track["title"])
    track_no = int(track.get("track_number", 0))

    filename = f"{track_no:02d} - {title}.mp3"
    return os.path.join(base_dir, artist, album, filename)


def download_audio(query, output):
    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-o",
        output.replace(".mp3", ".%(ext)s"),
        "--no-playlist",
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def local_match(fp, track):
    key = f"{track['artist']}::{track['title']}".lower()

    if key in cache:
        return is_match(fp, cache[key])

    return None


def store_fingerprint(fp, track):
    key = f"{track['artist']}::{track['title']}".lower()
    cache[key] = fp
    save_cache(cache)


def apply_tags(file_path, track):
    try:
        audio = EasyID3(file_path)
    except Exception:
        audio = EasyID3()

    audio["title"] = track["title"]
    audio["artist"] = track["artist"]
    audio["album"] = track["album"]
    audio["tracknumber"] = str(track.get("track_number", 0))
    audio.save(file_path)

    if track.get("art"):
        img = requests.get(track["art"]).content
        audio = ID3(file_path)
        audio["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=img,
        )
        audio.save()


def download(track, base_dir):
    path = build_path(track, base_dir)

    if os.path.exists(path):
        return True

    os.makedirs(os.path.dirname(path), exist_ok=True)

    queries = [
        f"{track['artist']} - {track['title']}",
        f"{track['title']} {track['artist']}",
    ]

    for q in queries:
        try:
            download_audio(q, path)

            fp = get_fingerprint(path)
            if not fp:
                os.remove(path)
                continue

            match = local_match(fp, track)

            # if known match → instant accept
            if match is True:
                apply_tags(path, track)
                return True

            # if known mismatch → retry
            if match is False:
                os.remove(path)
                continue

            # new track → accept and cache
            store_fingerprint(fp, track)
            apply_tags(path, track)
            return True

        except Exception:
            if os.path.exists(path):
                os.remove(path)

    return False
