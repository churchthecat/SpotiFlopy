import os
import json
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.cache/spotiflopy_state.json")


def load_state():
    # default structure
    state = {
        "completed": [],
        "last_sync": {}
    }

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                loaded = json.load(f)

                # merge safely (backward compatibility)
                if isinstance(loaded, dict):
                    state["completed"] = loaded.get("completed", [])
                    state["last_sync"] = loaded.get("last_sync", {})
        except Exception:
            print("⚠️ Corrupted state file, resetting...")

    return state


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def make_key(track):
    return f"{track['artist']}::{track['title']}"


def now_iso():
    return datetime.utcnow().isoformat()
