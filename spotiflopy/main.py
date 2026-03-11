import os
import csv
import yt_dlp
import spotipy
from pathlib import Path
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

DOWNLOAD_DIR = Path.home() / "Music" / "SpotiFlopy"
CSV_FILE = "songs.csv"


def get_spotify_client():
    scope = "user-library-read"

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            cache_path=".spotiflopy_token_cache"
        )
    )


def load_downloaded():
    if not os.path.exists(CSV_FILE):
        return set()

    with open(CSV_FILE, newline="") as f:
        return set(row[0] for row in csv.reader(f))


def save_downloaded(song):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([song])


def get_liked_songs(sp):
    results = sp.current_user_saved_tracks(limit=50)

    while results:
        for item in results["items"]:
            track = item["track"]
            artist = track["artists"][0]["name"]
            title = track["name"]
            album = track["album"]["name"]

            yield artist, title, album

        if results["next"]:
            results = sp.next(results)
        else:
            results = None


def download_song(artist, title, album):

    query = f"ytsearch1:{artist} {title}"

    folder = DOWNLOAD_DIR / artist / album
    folder.mkdir(parents=True, exist_ok=True)

    filename = str(folder / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,

        # AUTO BROWSER COOKIES (important fix)
        "cookiesfrombrowser": ("chromium", "chrome", "firefox", "brave"),

        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([query])


def main():

    print("\nSyncing Spotify liked songs...\n")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    sp = get_spotify_client()
    downloaded = load_downloaded()

    for artist, title, album in get_liked_songs(sp):

        song_id = f"{artist} - {title}"

        if song_id in downloaded:
            continue

        try:
            download_song(artist, title, album)
            save_downloaded(song_id)
            print(f"✔ {song_id}")

        except Exception as e:
            print(f"Failed: {song_id} ({e})")

    print("\nDownload complete.\n")


if __name__ == "__main__":
    main()