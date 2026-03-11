import os
import json
import subprocess
import sys
import re

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

CONFIG_DIR = os.path.expanduser("~/.config/spotiflopy")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


# -----------------------------
# Config
# -----------------------------

def ensure_config():

    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):

        print("\nFirst run setup\n")

        download_dir = input("Enter music download directory: ").strip()

        download_dir = os.path.expanduser(download_dir)

        os.makedirs(download_dir, exist_ok=True)

        with open(CONFIG_FILE, "w") as f:
            json.dump({"download_dir": download_dir}, f)

        print(f"\nDownload directory set to: {download_dir}\n")


def get_download_dir():

    ensure_config()

    with open(CONFIG_FILE) as f:
        config = json.load(f)

    return config["download_dir"]


def set_download_dir():

    new_dir = input("Enter new download directory: ").strip()

    new_dir = os.path.expanduser(new_dir)

    os.makedirs(new_dir, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump({"download_dir": new_dir}, f)

    print(f"\nDownload directory updated to: {new_dir}\n")


# -----------------------------
# Spotify
# -----------------------------

def get_spotify_client():

    load_dotenv()

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="user-library-read",
            open_browser=True
        )
    )


# -----------------------------
# Fetch songs
# -----------------------------

def fetch_liked_songs(sp):

    results = []
    offset = 0

    while True:

        items = sp.current_user_saved_tracks(limit=50, offset=offset)["items"]

        if not items:
            break

        for item in items:

            track = item["track"]

            artist = track["artists"][0]["name"]
            title = track["name"]
            album = track["album"]["name"]
            cover = track["album"]["images"][0]["url"]

            results.append((artist, title, album, cover))

        offset += 50

    return results


def fetch_playlist(sp, playlist_url):

    results = []

    playlist = sp.playlist_items(playlist_url)

    for item in playlist["items"]:

        track = item["track"]

        if not track:
            continue

        artist = track["artists"][0]["name"]
        title = track["name"]
        album = track["album"]["name"]
        cover = track["album"]["images"][0]["url"]

        results.append((artist, title, album, cover))

    return results


# -----------------------------
# Browser cookie detection
# -----------------------------

def detect_browser_cookie():

    browser_paths = {
        "chrome": "~/.config/google-chrome",
        "chromium": "~/.config/chromium",
        "brave": "~/.config/BraveSoftware/Brave-Browser",
        "firefox": "~/.mozilla/firefox"
    }

    for browser, path in browser_paths.items():

        expanded = os.path.expanduser(path)

        if os.path.exists(expanded):

            print(f"Using {browser} cookies for YouTube")

            return browser

    print("No browser cookies found — using anonymous downloads")

    return None


# -----------------------------
# Utils
# -----------------------------

def safe_filename(name):

    return re.sub(r'[\\/*?:"<>|]', "", name)


# -----------------------------
# Download
# -----------------------------

def download_song(song, browser_cookie):

    download_dir = get_download_dir()

    artist, title, album, cover = song

    artist = safe_filename(artist)
    title = safe_filename(title)

    artist_dir = os.path.join(download_dir, artist)

    os.makedirs(artist_dir, exist_ok=True)

    output_template = os.path.join(artist_dir, f"{title}.%(ext)s")
    final_mp3 = os.path.join(artist_dir, f"{title}.mp3")

    if os.path.exists(final_mp3):
        return

    query = f"ytsearch1:{artist} - {title}"

    cmd = [
        "yt-dlp",
        query,
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--embed-thumbnail",
        "--add-metadata",
        "--no-playlist",
        "-o", output_template
    ]

    if browser_cookie:

        cmd.extend(["--cookies-from-browser", browser_cookie])

    else:

        cmd.extend([
            "--sleep-requests", "1",
            "--sleep-interval", "2",
            "--max-sleep-interval", "5"
        ])

    try:

        subprocess.run(cmd, check=True)

        print(f"Downloaded: {artist} - {title}")

    except subprocess.CalledProcessError:

        print(f"Failed: {artist} - {title}")


# -----------------------------
# Sync
# -----------------------------

def sync_liked():

    print("\nSyncing Spotify liked songs...\n")

    sp = get_spotify_client()

    songs = fetch_liked_songs(sp)

    browser_cookie = detect_browser_cookie()

    for song in songs:

        download_song(song, browser_cookie)

    print("\nDownload complete.\n")


# -----------------------------
# CLI
# -----------------------------

def main():

    if len(sys.argv) > 1:

        cmd = sys.argv[1]

        if cmd == "setdir":

            set_download_dir()
            return

        if cmd == "playlist":

            if len(sys.argv) < 3:
                print("Usage: spotiflopy playlist PLAYLIST_URL")
                return

            playlist_url = sys.argv[2]

            sp = get_spotify_client()

            songs = fetch_playlist(sp, playlist_url)

            browser_cookie = detect_browser_cookie()

            for song in songs:
                download_song(song, browser_cookie)

            return

        if cmd == "sync":

            sync_liked()
            return

    sync_liked()


if __name__ == "__main__":
    main()