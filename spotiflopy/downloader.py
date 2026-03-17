import subprocess
from pathlib import Path
from .config import load_config, get_music_dir


def sanitize(text):
    return "".join(c for c in text if c.isalnum() or c in " .-_").strip()


def download(track):
    cfg = load_config()

    artist = sanitize(track["artist"])
    title = sanitize(track["title"])

    music_dir = Path(get_music_dir()).expanduser().resolve()
    music_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{artist} - {title}.%(ext)s"
    output = str(music_dir / filename)

    query = f"ytsearch1:{artist} {title}"

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", output,
        query
    ]

    # --- cookies handling ---
    if cfg.get("cookies_from_browser") and cfg["cookies_from_browser"] != "none":
        cmd += ["--cookies-from-browser", cfg["cookies_from_browser"]]
    elif cfg.get("cookies_file"):
        cmd += ["--cookies", cfg["cookies_file"]]

    # --- proxy ---
    if cfg.get("proxy"):
        cmd += ["--proxy", cfg["proxy"]]

    print(f"⬇️ Downloading: {artist} - {title}")
    subprocess.run(cmd)
