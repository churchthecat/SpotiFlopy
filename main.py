import os
import csv
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import yt_dlp
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

CONFIG_FILE = Path.home() / ".spotiflopy_config.json"
CSV_FILE = "songs.csv"

load_dotenv()


# -----------------------------
# Detect browser for cookies
# -----------------------------
def detect_browser():
    home = Path.home()

    paths = {
        "chrome": home / ".config/google-chrome",
        "chromium": home / ".config/chromium",
        "brave": home / ".config/BraveSoftware",
        "firefox": home / ".mozilla/firefox",
    }

    for browser, path in paths.items():
        if path.exists():
            print(f"Using browser cookies from: {browser}")
            return (browser,)

    print("No browser cookies found. Downloads may fail.")
    return None


BROWSER_COOKIES = detect_browser()


# -----------------------------
# Spotify
# -----------------------------
def get_spotify_client():
    auth_manager = SpotifyOAuth(
        scope="user-library-read",
        cache_path=".spotiflopy_token_cache"
    )

    return spotipy.Spotify(auth_manager=auth_manager)


# -----------------------------
# Config
# -----------------------------
def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)

    default_folder = str(Path.home() / "Desktop" / "Songs")

    folder = input(f"Download folder [{default_folder}]: ").strip()

    if not folder:
        folder = default_folder

    config = {"download_folder": folder}

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    return config


# -----------------------------
# Get Spotify liked tracks
# -----------------------------
def get_saved_tracks(sp):
    songs = []

    results = sp.current_user_saved_tracks(limit=50)

    while results:

        for item in results["items"]:
            track = item["track"]

            artist = track["artists"][0]["name"]
            title = track["name"]

            songs.append(f"{artist} - {title}")

        if results["next"]:
            results = sp.next(results)
        else:
            results = None

    return songs


# -----------------------------
# Track downloaded songs
# -----------------------------
def load_downloaded():
    if not Path(CSV_FILE).exists():
        return set()

    with open(CSV_FILE) as f:
        return set(row[0] for row in csv.reader(f))


def save_downloaded(song):
    with open(CSV_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([song])


# -----------------------------
# Download track
# -----------------------------
def download_track(song, folder, downloaded):

    if song in downloaded:
        return

    search = f"ytsearch1:{song}"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "ignoreerrors": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    if BROWSER_COOKIES:
        ydl_opts["cookiesfrombrowser"] = BROWSER_COOKIES

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search])

        save_downloaded(song)

        print(f"Downloaded: {song}")

    except Exception as e:

        print(f"Failed: {song}")
        print(e)


# -----------------------------
# Main
# -----------------------------
def main():

    sp = get_spotify_client()

    config = load_config()

    folder = config["download_folder"]

    Path(folder).mkdir(parents=True, exist_ok=True)

    songs = get_saved_tracks(sp)

    downloaded = load_downloaded()

    print(f"{len(songs)} songs found")
    print(f"{len(downloaded)} already downloaded")

    with ThreadPoolExecutor(max_workers=3) as executor:

        for song in songs:
            executor.submit(download_track, song, folder, downloaded)


if __name__ == "__main__":
    main()