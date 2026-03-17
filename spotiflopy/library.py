import json
from pathlib import Path

INDEX_FILE = Path.home() / ".spotiflopy_index.json"


def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump(list(index), f)


def exists(index, track_id):
    return track_id in index


def add(index, track_id):
    index.add(track_id)