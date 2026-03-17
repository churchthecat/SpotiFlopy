import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/spotiflopy/config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_music_dir():
    cfg = load_config()
    path = cfg.get("music_dir", "~/Music/SpotiFlopy")

    # 🔥 THIS IS THE IMPORTANT FIX
    return os.path.expanduser(path)
