import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILENAME = "config.json"


def load_config():
    # 1. Env vars
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if client_id and client_secret:
        return {
            "client_id": client_id,
            "client_secret": client_secret
        }

    # 2. config.json in cwd
    config_path = Path.cwd() / CONFIG_FILENAME

    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)

    raise FileNotFoundError(
        "No configuration found.\n\n"
        "Fix:\n"
        "1. Copy config.json.example -> config.json\n"
        "2. OR create a .env file with:\n\n"
        "SPOTIPY_CLIENT_ID=...\n"
        "SPOTIPY_CLIENT_SECRET=...\n"
    )


def get_music_dir():
    # Priority:
    # 1. ENV
    # 2. config.json
    # 3. default

    env_dir = os.getenv("SPOTIFLOPY_MUSIC_DIR")
    if env_dir:
        return env_dir

    try:
        cfg = load_config()
        if "music_dir" in cfg and cfg["music_dir"]:
            return cfg["music_dir"]
    except Exception:
        pass

    # Default fallback
    return str(Path.home() / "Music" / "SpotiFlopy")
