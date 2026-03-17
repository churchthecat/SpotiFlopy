import json
from pathlib import Path

CONFIG_PATH = Path.home() / "code" / "SpotiFlopy" / "config.json"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


# compatibility helpers
def get_config():
    return load_config()


def get_music_dir():
    cfg = load_config()
    return cfg["download_dir"]