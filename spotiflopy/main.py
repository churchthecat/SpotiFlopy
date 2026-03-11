import os
import subprocess
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC


DOWNLOAD_DIR = "downloads"
MAX_WORKERS = 4


def get_spotify_client():

    load_dotenv()

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not client_id or not client_secret:

        print("\nSpotify credentials missing.\n")
        print("Create a .env file:\n")
        print("SPOTIPY_CLIENT_ID=xxxx")
        print("SPOTIPY_CLIENT_SECRET=xxxx")
        print("SPOTIPY_REDIRECT_URI=http://localhost:8888/callback\n")

        exit(1)

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read playlist-read-private",
        )
    )


def detect_browser():

    browsers = ["chromium", "chrome", "brave", "edge"]

    for b in browsers:
        if shutil.which(b):
            return b

    return None


def get_cookie_args():

    browser = detect_browser()

    if browser:
        print(f"Using browser cookies: {browser}")
        return ["--cookies-from-browser", browser]

    if os.path.exists("cookies.txt"):
        print("Using cookies.txt")
        return ["--cookies", "cookies.txt"]

    print("No cookies found — downloads may fail")
    return []


def song_exists(artist, title):

    path = os.path.join(DOWNLOAD_DIR, artist, f"{title}.mp3")

    return os.path.exists(path)


def tag_mp3(file_path, artist, title, album=None, cover_url=None):

    try:
        audio = EasyID3(file_path)
    except:
        audio = EasyID3()
        audio.save(file_path)
        audio = EasyID3(file_path)

    audio["artist"] = artist
    audio["title"] = title

    if album:
        audio["album"] = album

    audio.save()

    if cover_url:

        try:
            img = requests.get(cover_url).content

            audio = ID3(file_path)

            audio["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=img,
            )

            audio.save()

        except:
            pass


def download_song(song, cookie_args):

    artist, title, album, cover = song

    if song_exists(artist, title):
        print(f"Skipping: {artist} - {title}")
        return

    query = f"{artist} {title}"

    output = os.path.join(DOWNLOAD_DIR, artist, f"{title}.%(ext)s")

    os.makedirs(os.path.dirname(output), exist_ok=True)

    base_cmd = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-o",
        output,
        f"ytsearch1:{query}",
    ]

    cmd = base_cmd + cookie_args

    try:

        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"Downloaded: {artist} - {title}")

    except subprocess.CalledProcessError:

        if cookie_args:

            print(f"Retry without cookies: {artist} - {title}")

            try:

                subprocess.run(
                    base_cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            except subprocess.CalledProcessError:

                print(f"Failed: {artist} - {title}")
                return

        else:

            print(f"Failed: {artist} - {title}")
            return

    mp3_path = os.path.join(DOWNLOAD_DIR, artist, f"{title}.mp3")

    if os.path.exists(mp3_path):
        tag_mp3(mp3_path, artist, title, album, cover)


def fetch_liked_songs(sp):

    songs = []
    offset = 0

    while True:

        results = sp.current_user_saved_tracks(limit=50, offset=offset)

        if not results["items"]:
            break

        for item in results["items"]:

            track = item["track"]

            artist = track["artists"][0]["name"]
            title = track["name"]
            album = track["album"]["name"]

            cover = None
            images = track["album"]["images"]

            if images:
                cover = images[0]["url"]

            songs.append((artist, title, album, cover))

        offset += 50

    return songs


def fetch_playlist(sp, playlist_url):

    songs = []
    results = sp.playlist_items(playlist_url)

    while results:

        for item in results["items"]:

            track = item["track"]

            if track is None:
                continue

            artist = track["artists"][0]["name"]
            title = track["name"]
            album = track["album"]["name"]

            cover = None
            images = track["album"]["images"]

            if images:
                cover = images[0]["url"]

            songs.append((artist, title, album, cover))

        if results["next"]:
            results = sp.next(results)
        else:
            results = None

    return songs


def run_downloads(songs):

    cookie_args = get_cookie_args()

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    print(f"\nDownloading {len(songs)} songs...\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(lambda s: download_song(s, cookie_args), songs)

    print("\nDone.\n")


def cmd_sync():

    print("\nSyncing Spotify liked songs...\n")

    sp = get_spotify_client()

    songs = fetch_liked_songs(sp)

    run_downloads(songs)


def cmd_playlist(url):

    print("\nDownloading playlist...\n")

    sp = get_spotify_client()

    songs = fetch_playlist(sp, url)

    run_downloads(songs)


def main():

    parser = argparse.ArgumentParser(
        prog="spotiflopy",
        description="Sync Spotify songs locally using YouTube",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("sync", help="Download liked songs")

    playlist_cmd = sub.add_parser("playlist", help="Download playlist")
    playlist_cmd.add_argument("url")

    args = parser.parse_args()

    if args.command == "sync":
        cmd_sync()

    elif args.command == "playlist":
        cmd_playlist(args.url)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()