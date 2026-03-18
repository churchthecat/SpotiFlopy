import argparse
import json
import os

from spotiflopy.download import sync_tracks, repair_library

CONFIG_PATH = os.path.expanduser("~/.spotiflopy_config.json")


# ----------------------------
# HELPERS
# ----------------------------
def clean(value):
    if not value:
        return value
    return value.strip().replace("\x7f", "")


def load_existing():
    if not os.path.exists(CONFIG_PATH):
        return {}

    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def prompt(name, current=None, secret=False):
    if current:
        if secret:
            display = "******"
        else:
            display = current
        val = input(f"{name} [{display}]: ").strip()
        return val if val else current
    else:
        return input(f"{name}: ").strip()


def validate_url(value, field):
    if not value.startswith("http"):
        raise RuntimeError(f"{field} must start with http/https")
    return value


# ----------------------------
# INIT (IMPROVED)
# ----------------------------
def init():
    print("🔧 SpotiFlopy Setup\n")

    existing = load_existing()

    client_id = prompt("Spotify Client ID", existing.get("spotify_client_id"), secret=True)
    client_secret = prompt("Spotify Client Secret", existing.get("spotify_client_secret"), secret=True)

    print("\nAuth mode:")
    print("1) Direct (manual redirect URI)")
    print("2) Proxy (recommended)")

    current_proxy = existing.get("proxy")
    current_redirect = existing.get("spotify_redirect_uri")

    mode = input(f"Choose [1/2] (current: {'proxy' if current_proxy else 'direct'}): ").strip()

    proxy = current_proxy
    redirect_uri = current_redirect

    if mode == "2" or (not mode and current_proxy):
        proxy = clean(prompt("Proxy base URL", current_proxy))
        proxy = validate_url(proxy, "Proxy")

        redirect_uri = proxy.rstrip("/") + "/callback"
        print(f"[AUTO] Redirect URI → {redirect_uri}")

    else:
        redirect_uri = clean(prompt("Spotify Redirect URI", current_redirect))
        redirect_uri = validate_url(redirect_uri, "Redirect URI")

        proxy = None

    music_dir = prompt("Music directory", existing.get("music_dir", "~/Music"))
    acoustid_key = prompt("AcoustID API Key (optional)", existing.get("acoustid_api_key"), secret=True)

    config = {
        "spotify_client_id": clean(client_id),
        "spotify_client_secret": clean(client_secret),
        "spotify_redirect_uri": clean(redirect_uri),
    }

    if proxy:
        config["proxy"] = clean(proxy)

    if music_dir:
        config["music_dir"] = clean(music_dir)

    if acoustid_key:
        config["acoustid_api_key"] = clean(acoustid_key)

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Config saved → {CONFIG_PATH}")


# ----------------------------
# CLI
# ----------------------------
def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init")

    sync = sub.add_parser("sync")
    sync.add_argument("--limit", type=int)

    repair = sub.add_parser("repair")
    repair.add_argument("--full", action="store_true")
    repair.add_argument("--fs", action="store_true")

    args = parser.parse_args()

    if args.cmd == "init":
        init()

    elif args.cmd == "sync":
        sync_tracks(limit=args.limit)

    elif args.cmd == "repair":
        repair_library(full=args.full, fs=args.fs)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
