#!/usr/bin/env bash
set -e

# ---------------- ACOUSTID MODULE ----------------
cat <<'PY' > spotiflopy/acoustid.py
import requests
import subprocess
from .config import load_config

API_URL = "https://api.acoustid.org/v2/lookup"


def get_fingerprint_and_duration(path):
    try:
        result = subprocess.run(
            ["fpcalc", path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None, None

        fp = None
        duration = None

        for line in result.stdout.splitlines():
            if line.startswith("FINGERPRINT="):
                fp = line.split("=", 1)[1]
            if line.startswith("DURATION="):
                duration = line.split("=", 1)[1]

        return fp, duration
    except Exception:
        return None, None


def lookup_acoustid(path):
    cfg = load_config()
    key = cfg.get("acoustid_key")

    if not key:
        return None

    fp, duration = get_fingerprint_and_duration(path)

    if not fp or not duration:
        return None

    try:
        r = requests.get(API_URL, params={
            "client": key,
            "fingerprint": fp,
            "duration": duration,
            "meta": "recordings"
        }, timeout=10)

        data = r.json()

        results = []

        for res in data.get("results", []):
            for rec in res.get("recordings", []):
                title = rec.get("title", "")
                artists = [a["name"] for a in rec.get("artists", [])]
                results.append((artists, title))

        return results

    except Exception:
        return None
PY

# ---------------- MATCHER UPGRADE ----------------
cat <<'PY' > spotiflopy/matcher.py
import os
from .fingerprint import get_fingerprint, load_cache, save_cache
from .acoustid import lookup_acoustid

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum() or c.isspace()).strip()


def build_index(base_dir):
    index = {}
    files = []

    for root, _, fs in os.walk(base_dir):
        for f in fs:
            if not f.endswith(".mp3"):
                continue
            path = os.path.join(root, f)
            files.append(path)
            index[normalize(f)] = path

    return index, files


def match_acoustid(track, candidates):
    target_artist = normalize(track["artist"])
    target_title = normalize(track["title"])

    for path in candidates:
        results = lookup_acoustid(path)
        if not results:
            continue

        for artists, title in results:
            a = normalize(" ".join(artists))
            t = normalize(title)

            if target_title in t and target_artist in a:
                return path

    return None


def find_in_index(index_data, track):
    index, files = index_data

    query = normalize(f"{track['artist']} {track['title']}")

    # 1. fast filename match
    for k, path in index.items():
        if query in k:
            return path

    # 2. fingerprint cache match
    cache = load_cache()
    for path in files:
        fp = get_fingerprint(path, cache)
        if not fp:
            continue

        if query[:10] in fp:
            save_cache(cache)
            return path

    save_cache(cache)

    # 3. acoustid (slow but accurate)
    print("🧬 AcoustID matching...")
    match = match_acoustid(track, files)
    if match:
        return match

    return None
PY

pip install requests
pip install -e .

echo "AcoustID system installed."
