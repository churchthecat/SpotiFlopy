import os
import subprocess
import json
import requests

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

from .fingerprint import load_cache, save_cache, get_fingerprint, is_match

FP_CACHE = load_cache()

CACHE_FILE = ".spotiflopy_cache.json"


def load_db():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_db(db):
    with open(CACHE_FILE, "w") as f:
        json.dump(db, f, indent=2)


DB = load_db()


def safe(s):
    return "".join(c for c in s if c not in '/\\?%*:|"<>').strip()


def normalize(s):
    return s.lower().replace("&", "and")


def build_path(track, base_dir):
    artist = safe(track["artist"])
    album = safe(track["album"])
    title = safe(track["title"])
    track_no = int(track.get("track_number", 0))

    filename = f"{track_no:02d} - {title}.mp3"
    return os.path.join(base_dir, artist, album, filename)


# -----------------------
# MATCHING (CACHED)
# -----------------------

def search_youtube(query, limit=5):
    cmd = [
        "yt-dlp",
        f"ytsearch{limit}:{query}",
        "--dump-json",
        "--skip-download",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    results = []
    for line in proc.stdout.splitlines():
        try:
            results.append(json.loads(line))
        except:
            pass

    return results


def score_result(video, track):
    score = 0

    title = normalize(video.get("title", ""))
    uploader = normalize(video.get("uploader", ""))

    artist = normalize(track["artist"])
    song = normalize(track["title"])

    if artist in title or artist in uploader:
        score += 40

    if song in title:
        score += 40

    duration = video.get("duration")
    if duration and track.get("duration"):
        if abs(duration - track["duration"]) < 5:
            score += 15

    if "official" in title:
        score += 5

    if "vevo" in uploader or "official" in uploader:
        score += 10

    return score


def best_match(track):
    key = track["id"]

    # 🔥 CACHE HIT (NO SEARCH)
    if key in DB and DB[key].get("url"):
        return DB[key]["url"]

    query = f"{track['artist']} {track['title']}"
    results = search_youtube(query)

    best = None
    best_score = 0

    for r in results:
        s = score_result(r, track)

        if s > best_score:
            best_score = s
            best = r

    if not best or best_score < 50:
        return None

    url = best["webpage_url"]

    DB.setdefault(key, {})["url"] = url
    save_db(DB)

    return url


# -----------------------
# TAGGING
# -----------------------

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
        try:
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
        except:
            pass


# -----------------------
# MAIN PIPELINE (ULTRA FAST)
# -----------------------

def download(track, base_dir):
    key = track["id"]
    path = build_path(track, base_dir)

    # 🔥 INSTANT SKIP (NO FS / NO SEARCH)
    if key in DB and os.path.exists(DB[key].get("file", "")):
        return True

    if os.path.exists(path):
        DB.setdefault(key, {})["file"] = path
        save_db(DB)
        return True

    os.makedirs(os.path.dirname(path), exist_ok=True)

    url = best_match(track)
    if not url:
        return False

    try:
        cmd = [
            "yt-dlp",
            url,
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "-o",
            path.replace(".mp3", ".%(ext)s"),
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        fp = get_fingerprint(path)
        if not fp:
            os.remove(path)
            return False

        # 🔥 CACHE MATCH (NO API)
        if key in FP_CACHE:
            if not is_match(fp, FP_CACHE[key]):
                os.remove(path)
                return False

        FP_CACHE[key] = fp
        save_cache(FP_CACHE)

        apply_tags(path, track)

        DB.setdefault(key, {})["file"] = path
        DB[key]["fingerprint"] = fp
        save_db(DB)

        return True

    except Exception:
        if os.path.exists(path):
            os.remove(path)
        return False
