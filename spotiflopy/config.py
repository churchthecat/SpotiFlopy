import os
import json

CONFIG_PATH = os.path.expanduser("~/.spotiflopy.json")


DEFAULT_CONFIG = {
    "client_id": "",
    "client_secret": "",
    "redirect_uri": "http://127.0.0.1:8888/callback",
    "music_dir": "~/Music",
    "backend": "yt-dlp",
    "cookies_from_browser": "chromium",
    "cookies_file": "",
    "proxy": "",
    "acoustid_key": ""
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)

    # merge defaults (important for upgrades)
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    return merged


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get_music_dir():
    return os.path.expanduser(load_config()["music_dir"])
