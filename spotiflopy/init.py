import json
import os

CONFIG_PATH = os.path.expanduser("~/.spotiflopy_config.json")


def ask(prompt, default=None, optional=False):
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value or default
    value = input(f"{prompt}: ").strip()
    if optional and value == "":
        return None
    return value


def run_init():
    print("🔧 SpotiFlopy Setup\n")

    cfg = {}

    cfg["spotify_client_id"] = ask("Spotify Client ID")
    cfg["spotify_client_secret"] = ask("Spotify Client Secret")

    cfg["spotify_redirect_uri"] = ask(
        "Spotify Redirect URI",
        "http://127.0.0.1:9090/callback"
    )

    cfg["proxy"] = ask(
        "Proxy (optional, e.g. http://127.0.0.1:8080)",
        optional=True
    )

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"\n✅ Config saved to {CONFIG_PATH}")
    print("⚠️ Make sure redirect URI is added in Spotify Dashboard!")
