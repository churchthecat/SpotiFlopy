import os
import csv
import json
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import yt_dlp
import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

CONFIG_FILE = Path.home() / ".spotiflopy_config.json"
CSV_FILE = "songs.csv"

load_dotenv()


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
            print(f"Using browser cookies: {browser}")
            return (browser,)

    print("No browser cookies found")
    return None


BROWSER = detect_browser()


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
    if not Path(CSV_FILE).exists():
        return set()

    with open(CSV_FILE) as f:
        return set(row[0] for row in csv.reader(f))


def save_downloaded(song):

    with open(CSV_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([song])


def download_art(url):

    r = requests.get(url)

    tmp = tempfile.NamedTemporaryFile(delete=False)

    tmp.write(r.content)

    tmp.close()

    return tmp.name


def tag_file(path, track):

    audio = EasyID3(path)

    audio["title"] = track["name"]
    audio["artist"] = track["artists"][0]["name"]
    audio["album"] = track["album"]["name"]
    audio["tracknumber"] = str(track["track_number"])

    audio.save()

    artwork = track["album"]["images"][0]["url"]

    art_file = download_art(artwork)

    audio = ID3(path)

    with open(art_file, "rb") as f:

        audio.add(
            APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=f.read(),
            )
        )

    audio.save()

    os.remove(art_file)


def download_track(track, root_folder, downloaded):

    artist = track["artists"][0]["name"]
    album = track["album"]["name"]
    title = track["name"]

    song_id = track["id"]

    if song_id in downloaded:
        return

    folder = Path(root_folder) / artist / album

    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{track['track_number']:02d} - {title}.mp3"

    output = folder / filename

    search = f"ytsearch1:{artist} {title} audio"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output),
        "noplaylist": True,
        "quiet": True,
        "ignoreerrors": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    if BROWSER:
        ydl_opts["cookiesfrombrowser"] = BROWSER

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search])

        tag_file(output, track)

        save_downloaded(song_id)

        print(f"Downloaded: {artist} - {title}")

    except Exception as e:

        print(f"Failed: {artist} - {title}")
        print(e)


def get_saved_tracks(sp):

    tracks = []

    results = sp.current_user_saved_tracks(limit=50)

    while results:

        for item in results["items"]:
            tracks.append(item["track"])

        if results["next"]:
            results = sp.next(results)
        else:
            results = None

    return tracks


def main():

    sp = get_spotify_client()

    config = load_config()

    root = config["download_folder"]

    Path(root).mkdir(parents=True, exist_ok=True)

    tracks = get_saved_tracks(sp)

    downloaded = load_downloaded()

    print(f"{len(tracks)} tracks found")

    with ThreadPoolExecutor(max_workers=3) as executor:

        for track in tracks:
            executor.submit(download_track, track, root, downloaded)


if __name__ == "__main__":
    main()