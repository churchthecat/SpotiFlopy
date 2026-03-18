import os
import json

CONFIG_PATH = os.path.expanduser("~/.spotiflopy_config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}

    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CONFIG ERROR] {e}")
        return {}


def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[CONFIG ERROR] {e}")
