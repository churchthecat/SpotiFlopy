from .config import load_config, save_config


def run_init():
    cfg = load_config()

    print("🎧 SpotiFlopy Setup\n")

    def ask(key, label, default=None, secret=False):
        current = cfg.get(key, "")
        prompt = f"{label}"
        if current:
            prompt += f" [{current}]"
        if default:
            prompt += f" (default: {default})"
        prompt += ": "

        val = input(prompt).strip()
        if val:
            return val
        if current:
            return current
        return default or ""

    cfg["client_id"] = ask("client_id", "Spotify Client ID")
    cfg["client_secret"] = ask("client_secret", "Spotify Client Secret")
    cfg["redirect_uri"] = ask(
        "redirect_uri",
        "Redirect URI",
        "http://127.0.0.1:8888/callback"
    )

    cfg["music_dir"] = ask("music_dir", "Music directory", "~/Music")

    print("\n(Optional) Better matching:")
    print("👉 Get key at https://acoustid.org/api-key")

    cfg["acoustid_key"] = ask(
        "acoustid_key",
        "AcoustID API Key (optional)"
    )

    save_config(cfg)

    print("\n✅ Config saved to ~/.spotiflopy.json")
