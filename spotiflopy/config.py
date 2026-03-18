import json
import os


def get_config_path():
    # priority:
    # 1. local project
    # 2. home config

    local = os.path.join(os.getcwd(), "config.json")
    home = os.path.expanduser("~/.config/spotiflopy/config.json")

    if os.path.exists(local):
        return local
    if os.path.exists(home):
        return home

    return local  # default


def load_config():
    path = get_config_path()

    if not os.path.exists(path):
        raise Exception(
            "No config.json found. Run: spotiflopy init"
        )

    with open(path) as f:
        config = json.load(f)

    # validate
    required = ["spotify_client_id", "spotify_client_secret"]

    for key in required:
        if key not in config or not config[key]:
            raise Exception(f"Missing config key: {key}")

    return config
