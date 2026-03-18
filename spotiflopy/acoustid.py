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
