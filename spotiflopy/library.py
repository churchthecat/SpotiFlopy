import os
import json


LIBRARY_FILE = os.path.expanduser("~/.spotiflopy_library.json")


def get_all_tracks():
    if not os.path.exists(LIBRARY_FILE):
        print("[WARN] No library file found, returning empty list")
        return []

    try:
        with open(LIBRARY_FILE, "r") as f:
            data = json.load(f)
            return data.get("tracks", [])
    except Exception as e:
        print(f"[ERROR] Failed to load library: {e}")
        return []


def save_library(tracks):
    data = {"tracks": tracks}

    with open(LIBRARY_FILE, "w") as f:
        json.dump(data, f, indent=2)
