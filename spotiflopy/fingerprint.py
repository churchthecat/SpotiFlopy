import os
import json
import subprocess

CACHE_FILE = os.path.expanduser("~/.spotiflopy_fingerprints.json")


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def get_fingerprint(file_path):
    try:
        result = subprocess.run(
            ["fpcalc", file_path],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if line.startswith("FINGERPRINT="):
                return line.split("=", 1)[1]

    except Exception:
        return None


def is_match(fp1, fp2):
    if not fp1 or not fp2:
        return False

    # simple similarity check (fast)
    return fp1[:100] == fp2[:100]
