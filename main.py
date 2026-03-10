import os
import json
import shutil
import socket
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from yt_dlp import YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
from dotenv import load_dotenv


# -------------------------
# CONFIG
# -------------------------

DEFAULT_BASE_PATH = Path.home() / "Music" / "Spotiflopy"
CONFIG_FILE = Path.home() / ".spotiflopy_config.json"
TOKEN_CACHE = Path.home() / ".spotiflopy_token_cache"

MAX_WORKERS = 4
scope = "user-library-read"


# -------------------------
# Dependency Check
# -------------------------

def check_dependencies():

    if not shutil.which("ffmpeg"):
        print("FFmpeg missing")
        print("Install with: sudo apt install ffmpeg")
        exit()

    try:
        socket.create_connection(("youtube.com", 80), timeout=5)
    except OSError:
        print("No internet connection")
        exit()


# -------------------------
# Config
# -------------------------

def load_config():

    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())

    return {}


def save_config(config):
    CONFIG_FILE.write_text(json.dumps(config, indent=4))


def choose_download_folder():

    config = load_config()

    if "base_path" in config:
        p = Path(config["base_path"])
        p.mkdir(parents=True, exist_ok=True)
        return p

    folder = input("Download folder (enter for ~/Music/Spotiflopy): ")

    if not folder:
        folder = DEFAULT_BASE_PATH

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    config["base_path"] = str(folder)
    save_config(config)

    return folder


# -------------------------
# Spotify
# -------------------------

def spotify_client():

    load_dotenv()

    auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=scope,
        cache_handler=CacheFileHandler(cache_path=str(TOKEN_CACHE)),
        open_browser=True
    )

    return spotipy.Spotify(auth_manager=auth)


# -------------------------
# Helpers
# -------------------------

def sanitize(text):

    text = text.replace("/", " - ")
    text = text.replace("\\", " - ")

    text = re.sub(r'[<>:"|?*]', '', text)

    return text.strip()


def clean_title(text):

    text = text.lower()

    text = re.sub(r"\(.*?\)", "", text)

    banned = [
        "live",
        "cover",
        "remix",
        "karaoke",
        "instrumental",
        "lyrics",
        "tribute"
    ]

    for b in banned:
        if b in text:
            return None

    return text


# -------------------------
# YouTube Search
# -------------------------

def find_best_youtube(track, artist, duration):

    query = f"{artist} {track}"

    with YoutubeDL({"quiet": True}) as ydl:

        info = ydl.extract_info(
            f"ytsearch10:{query}",
            download=False
        )

    best_video = None
    best_score = 999999

    for entry in info["entries"]:

        if not entry:
            continue

        title = clean_title(entry["title"])

        if not title:
            continue

        yt_duration = entry.get("duration")

        if not yt_duration:
            continue

        diff = abs(yt_duration - duration)

        if diff < best_score:
            best_score = diff
            best_video = entry["id"]

    if best_video:
        return f"https://www.youtube.com/watch?v={best_video}"

    raise Exception("No suitable YouTube match")


# -------------------------
# Spotify Tracks
# -------------------------

def get_liked_songs(sp):

    results = sp.current_user_saved_tracks(limit=50)

    songs = []

    while results:

        for item in results["items"]:

            track = item["track"]

            songs.append(
                (
                    track["name"],
                    track["artists"][0]["name"],
                    track["album"]["name"],
                    track["track_number"],
                    int(track["duration_ms"] / 1000)
                )
            )

        results = sp.next(results) if results["next"] else None

    return songs


# -------------------------
# File Check
# -------------------------

def already_downloaded(base, artist, album, number, track):

    path = base / sanitize(artist) / sanitize(album) / f"{number:02d} - {sanitize(track)}.mp3"

    return path.exists()


# -------------------------
# Download
# -------------------------

def download_song(base, track, artist, album, number, duration):

    artist_folder = base / sanitize(artist)
    album_folder = artist_folder / sanitize(album)

    album_folder.mkdir(parents=True, exist_ok=True)

    output_template = str(
        album_folder / f"{number:02d} - {sanitize(track)}.%(ext)s"
    )

    youtube_url = find_best_youtube(track, artist, duration)

    ydl_opts = {

        "format": "bestaudio/best",

        "outtmpl": output_template,

        "cookiefile": "cookies.txt",

        "retries": 10,
        "fragment_retries": 10,

        "sleep_interval": 2,
        "max_sleep_interval": 5,

        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        },

        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"}
        ],

        "addmetadata": True,
        "embedthumbnail": True,
        "quiet": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    print(f"Downloaded: {track} - {artist}")


# -------------------------
# Worker
# -------------------------

def worker(base, song):

    track, artist, album, number, duration = song

    if already_downloaded(base, artist, album, number, track):

        print(f"Skipping: {track} - {artist}")
        return

    try:

        download_song(base, track, artist, album, number, duration)

    except Exception as e:

        print(f"FAILED: {track} - {artist} -> {e}")


# -------------------------
# Main
# -------------------------

def main():

    check_dependencies()

    base = choose_download_folder()

    sp = spotify_client()

    songs = get_liked_songs(sp)

    print(f"\nFound {len(songs)} liked songs\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        for song in songs:
            executor.submit(worker, base, song)


if __name__ == "__main__":
    main()