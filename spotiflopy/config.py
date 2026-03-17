import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILENAME = "config.json"


def load_config():
    # 1. Try environment variables first
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if client_id and client_secret:
        return {
            "client_id": client_id,
            "client_secret": client_secret
        }

    # 2. Try config.json in current working directory
    config_path = Path.cwd() / CONFIG_FILENAME

    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)

    # 3. Fail with helpful message
    raise FileNotFoundError(
        "No configuration found.\n\n"
        "Fix:\n"
        "1. Copy config.json.example → config.json\n"
        "2. OR create a .env file with:\n\n"
        "   SPOTIPY_CLIENT_ID=...\n"
        "   SPOTIPY_CLIENT_SECRET=...\n"
    )
