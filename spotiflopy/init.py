from .config import load_config, save_config


def choose(prompt, options, default):
    options_str = "/".join(options)

    while True:
        val = input(f"{prompt} ({options_str}) [{default}]: ").strip().lower()

        if not val:
            return default

        if val in options:
            return val

        print(f"❌ Invalid choice. Options: {options_str}")


def ask(prompt, default=""):
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default


def run_init():
    cfg = load_config()

    print("🎧 SpotiFlopy Setup\n")

    cfg["client_id"] = ask("Spotify Client ID", cfg.get("client_id", ""))
    cfg["client_secret"] = ask("Spotify Client Secret", cfg.get("client_secret", ""))
    cfg["redirect_uri"] = ask(
        "Redirect URI",
        cfg.get("redirect_uri", "http://127.0.0.1:8888/callback")
    )

    cfg["music_dir"] = ask("Music directory", cfg.get("music_dir", "~/Music"))

    print("\n🔍 Matching (optional but recommended)")
    print("Get API key: https://acoustid.org/api-key")

    cfg["acoustid_key"] = ask(
        "AcoustID API Key",
        cfg.get("acoustid_key", "")
    )

    print("\n🎧 Audio format:")
    print("mp3  = compatible, smaller")
    print("flac = lossless container (bigger)")
    print("best = auto best source")

    cfg["audio_format"] = choose(
        "Select format",
        ["mp3", "flac", "best"],
        cfg.get("audio_format", "mp3")
    )

    if cfg["audio_format"] == "mp3":
        cfg["audio_quality"] = choose(
            "MP3 quality",
            ["128", "192", "256", "320"],
            cfg.get("audio_quality", "320")
        )
    else:
        cfg["audio_quality"] = "best"

    save_config(cfg)

    print("\n✅ Configuration saved to ~/.spotiflopy.json")
