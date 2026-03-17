import json
import os
from pathlib import Path

CONFIG_PATH = Path.cwd() / "config.json"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config not found at {CONFIG_PATH}. Run 'spotiflopy init' first."
        )

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_music_dir():
    env_dir = os.getenv("SPOTIFLOPY_MUSIC_DIR")
    if env_dir:
        return env_dir

    try:
        cfg = load_config()
        return cfg.get("music_dir") or "~/Music/SpotiFlopy"
    except Exception:
        return "~/Music/SpotiFlopy"
