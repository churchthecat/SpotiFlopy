import os
import json
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

CONFIG_DIR = os.path.expanduser("~/.config/spotiflopy")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def ensure_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        print("\nFirst run setup\n")
        download_dir = input("Enter music download directory: ").strip()

        if download_dir.startswith("~"):
            download_dir = os.path.expanduser(download_dir)

        os.makedirs(download_dir, exist_ok=True)

        config = {"download_dir": download_dir}

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

        print(f"\nDownload directory set to: {download_dir}\n")


def get_download_dir():
    ensure_config()

    with open(CONFIG_FILE) as f:
        return json.load(f)["download_dir"]


def set_download_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    new_dir = input("Enter new music download directory: ").strip()

    if new_dir.startswith("~"):
        new_dir = os.path.expanduser(new_dir)

    os.makedirs(new_dir, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump({"download_dir": new_dir}, f)

    print(f"\nDownload directory updated to: {new_dir}\n")


def get_spotify_client():
    load_dotenv()

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="user-library-read",
            open_browser=True
        )
    )


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
    playlist = sp.playlist_items(playlist_url)
    results = []

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


def detect_browser_cookie():
    browsers = ["chrome", "chromium", "brave"]

    for browser in browsers:
        try:
            subprocess.run(
                ["yt-dlp", "--cookies-from-browser", browser, "--skip-download", "https://youtube.com"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            return browser
        except Exception:
            continue

    return None


def download_song(song, browser_cookie):
    download_dir = get_download_dir()

    artist, title, album, cover = song

    folder = os.path.join(download_dir, artist)
    os.makedirs(folder, exist_ok=True)

    output = os.path.join(folder, f"{title}.%(ext)s")
    mp3_path = os.path.join(folder, f"{title}.mp3")

    if os.path.exists(mp3_path):
        return

    query = f"ytsearch1:{artist} - {title}"

    cmd = [
        "yt-dlp",
        query,
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-o",
        output,
        "--embed-thumbnail",
        "--add-metadata",
        "--no-playlist"
    ]

    if browser_cookie:
        cmd.extend(["--cookies-from-browser", browser_cookie])

    try:
        subprocess.run(cmd, check=True)
        print(f"Downloaded: {artist} - {title}")
    except Exception as e:
        print(f"Failed: {artist} - {title} ({e})")


def sync_liked():
    print("\nSyncing Spotify liked songs...\n")

    sp = get_spotify_client()

    songs = fetch_liked_songs(sp)

    browser_cookie = detect_browser_cookie()

    for song in songs:
        download_song(song, browser_cookie)

    print("\nDownload complete.\n")


def main():
    import sys

    if len(sys.argv) > 1:

        if sys.argv[1] == "setdir":
            set_download_dir()
            return

        if sys.argv[1] == "playlist":
            playlist_url = sys.argv[2]

            sp = get_spotify_client()

            songs = fetch_playlist(sp, playlist_url)

            browser_cookie = detect_browser_cookie()

            for song in songs:
                download_song(song, browser_cookie)

            return

    sync_liked()


if __name__ == "__main__":
    main()