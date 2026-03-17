import subprocess
import json
import os

CACHE_FILE = os.path.expanduser("~/.cache/spotiflopy_fingerprints.json")


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def get_fingerprint(path, cache):
    if path in cache:
        return cache[path]

    try:
        result = subprocess.run(
            ["fpcalc", path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            if line.startswith("FINGERPRINT="):
                fp = line.split("=", 1)[1]
                cache[path] = fp
                return fp

    except Exception:
        return None

    return None
