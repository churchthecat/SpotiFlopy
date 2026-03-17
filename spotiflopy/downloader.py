import subprocess
from pathlib import Path
from .config import get_music_dir


def sanitize(name):
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("---- yt-dlp ERROR ----")
        print(result.stderr.strip())
        print("----------------------")

    return result


def build_base_cmd(search, filepath):
    return [
        "yt-dlp",
        f"ytsearch1:{search}",

        # Format (audio only)
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192",

        # Stability
        "--no-playlist",
        "--ignore-errors",
        "--no-warnings",

        # Reduce bot detection
        "--user-agent", "Mozilla/5.0",
        "--sleep-interval", "1",
        "--max-sleep-interval", "3",

        # Metadata
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails", "jpg",

        "-o", str(filepath)
    ]


def download(track):
    artist = sanitize(track["artist"])
    title = sanitize(track["track"])
    album = sanitize(track.get("album", "Unknown Album"))

    music_dir = Path(get_music_dir())
    album_dir = music_dir / artist / album
    album_dir.mkdir(parents=True, exist_ok=True)

    filepath = album_dir / f"{title}.mp3"

    if filepath.exists():
        print(f"Skipping (exists): {artist} - {title}")
        return

    # 🔥 Better search query
    search = f"{artist} - {title} official audio -live -remix -cover"
    print(f"\nSearching: {search}")

    base_cmd = build_base_cmd(search, filepath)

    # ---- STRATEGY 1: Chromium cookies ----
    print("Trying Chromium cookies...")
    cmd_chromium = base_cmd + [
        "--cookies-from-browser", "chromium"
    ]

    result = run(cmd_chromium)
    if result.returncode == 0 and filepath.exists():
        print(f"Downloaded (chromium): {artist} - {title}")
        return

    # ---- STRATEGY 2: cookies.txt fallback ----
    print("Falling back to cookies.txt...")

    cookies_file = Path("cookies.txt")
    if not cookies_file.exists():
        print("cookies.txt not found, skipping fallback")
    else:
        cmd_cookies = base_cmd + [
            "--cookies", "cookies.txt"
        ]

        result = run(cmd_cookies)
        if result.returncode == 0 and filepath.exists():
            print(f"Downloaded (cookies.txt): {artist} - {title}")
            return

    # ---- STRATEGY 3: Retry with delay ----
    print("Retrying with cookies.txt + delay...")

    if cookies_file.exists():
        cmd_retry = base_cmd + [
            "--cookies", "cookies.txt",
            "--sleep-interval", "2",
            "--max-sleep-interval", "5"
        ]

        result = run(cmd_retry)
        if result.returncode == 0 and filepath.exists():
            print(f"Downloaded (retry): {artist} - {title}")
            return

    raise Exception("Download failed after all strategies")
