import json
import os

CONFIG_PATH = os.path.expanduser("~/.spotiflopy.json")


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}

    with open(CONFIG_PATH) as f:
        return json.load(f)
