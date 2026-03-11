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


def get_spotify_client():
    auth_manager = SpotifyOAuth(
        scope="user-library-read",
        cache_path=".spotiflopy_token_cache"
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)

    default_folder = str(Path.home() / "Music" / "SpotiFlopy")
    folder = input(f"Download folder [{default_folder}]: ").strip()

    if not folder:
        folder = default_folder

    config = {"download_folder": folder}

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    return config


def load_downloaded():
    downloaded = set()

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.reader(f)
            for row in reader:
                downloaded.add(row[0])

    return downloaded


def save_downloaded(track_id):
    with open(CSV_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([track_id])


def search_youtube(query):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "default_search": "ytsearch1"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

    return info["entries"][0]["webpage_url"]


def download_track(track, folder, downloaded):
    track_id = track["id"]

    if track_id in downloaded:
        return

    artist = track["artists"][0]["name"]
    title = track["name"]
    album = track["album"]["name"]

    query = f"{artist} {title} audio"

    try:
        url = search_youtube(query)

        artist_dir = Path(folder) / artist
        album_dir = artist_dir / album

        album_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(album_dir / "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "cookiesfrombrowser": ("chromium",),
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        save_downloaded(track_id)

        print(f"Downloaded: {artist} - {title}")

    except Exception as e:
        print(f"Failed: {artist} - {title} ({e})")


def get_liked_tracks(sp):
    results = sp.current_user_saved_tracks(limit=50)
    songs = []

    while results:
        for item in results["items"]:
            songs.append(item["track"])

        if results["next"]:
            results = sp.next(results)
        else:
            results = None

    return songs


def sync():
    config = load_config()
    folder = config["download_folder"]

    downloaded = load_downloaded()

    sp = get_spotify_client()

    songs = get_liked_tracks(sp)

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(lambda t: download_track(t, folder, downloaded), songs)


def main():
    print("Syncing Spotify liked songs...")
    sync()


if __name__ == "__main__":
    main()