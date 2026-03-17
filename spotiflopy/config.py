import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/spotiflopy/config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)

    # expand paths
    if "music_dir" in cfg:
        cfg["music_dir"] = os.path.expanduser(cfg["music_dir"])

    return cfg


def get_music_dir():
    cfg = load_config()

    music_dir = cfg.get("music_dir")
    if not music_dir:
        raise ValueError("music_dir not set in config")

    return music_dir
