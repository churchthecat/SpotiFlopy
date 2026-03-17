import subprocess
from pathlib import Path
from .config import load_config, get_music_dir


def sanitize(text):
    if not text:
        return ""

    cleaned = "".join(c for c in text if c.isalnum() or c in " .-_()").strip()
    cleaned = " ".join(cleaned.split())
    return cleaned


def file_exists(album_dir, track_no, title):
    return (album_dir / f"{track_no:02d} - {title}.mp3").exists()


def download(track):
    cfg = load_config()

    artist = sanitize(track["artist"])
    title = sanitize(track["title"])
    track_no = track.get("track_number", 0)

    # --- album handling (no Unknown Album ever) ---
    raw_album = track.get("album")
    if raw_album:
        album = sanitize(raw_album)
    else:
        album = "Singles"

    if not album:
        album = "Singles"

    music_dir = Path(get_music_dir()).expanduser().resolve()
    album_dir = music_dir / artist / album
    album_dir.mkdir(parents=True, exist_ok=True)

    # --- skip existing ---
    if file_exists(album_dir, track_no, title):
        print(f"✔ Skipping: {artist} - {title}")
        return

    # enforce filename ourselves (yt-dlp must NOT override this)
    filename = f"{track_no:02d} - {title}.mp3"
    output = str(album_dir / filename)

    query = f"ytsearch1:{artist} {title} audio"

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",

        # embed metadata + cover art INTO file
        "--embed-thumbnail",
        "--add-metadata",

        # do NOT let yt-dlp rename files
        "--no-playlist",

        "-o", output,
        query
    ]

    # --- cookies ---
    if cfg.get("cookies_from_browser") and cfg["cookies_from_browser"] != "none":
        cmd += ["--cookies-from-browser", cfg["cookies_from_browser"]]
    elif cfg.get("cookies_file"):
        cmd += ["--cookies", cfg["cookies_file"]]

    # --- proxy ---
    if cfg.get("proxy"):
        cmd += ["--proxy", cfg["proxy"]]

    print(f"⬇️ Downloading: {artist} - {title}")
    subprocess.run(cmd)
