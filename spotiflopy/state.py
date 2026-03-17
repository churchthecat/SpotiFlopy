import json
import os
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.spotiflopy_state.json")


def now_iso():
    return datetime.utcnow().isoformat()


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"completed": [], "last_sync": {}}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def make_key(track):
    # STRONG UNIQUE KEY → Spotify ID
    if "id" in track and track["id"]:
        return f"spotify:{track['id']}"

    # fallback (should rarely happen)
    return f"{track['artist']}::{track['title']}".lower()
