import os
import subprocess
import shutil
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


DOWNLOAD_DIR = "downloads"


def get_spotify_client():
    load_dotenv()

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not client_id or not client_secret:
        print("\nSpotify credentials missing.\n")
        print("Create a .env file with:\n")
        print("SPOTIPY_CLIENT_ID=your_client_id")
        print("SPOTIPY_CLIENT_SECRET=your_client_secret")
        print("SPOTIPY_REDIRECT_URI=http://localhost:8888/callback\n")
        exit(1)

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read"
        )
    )


def detect_browser():
    browsers = [
        "chrome",
        "chromium",
        "brave",
        "edge"
    ]

    for b in browsers:
        if shutil.which(b):
            return b

    return None


def download_song(artist, title, browser=None):

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
        f"ytsearch1:{query}"
    ]

    if browser:
        cmd = base_cmd + ["--cookies-from-browser", browser]
    else:
        cmd = base_cmd

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Downloaded: {artist} - {title}")

    except subprocess.CalledProcessError:

        if browser:
            print(f"Retrying without cookies: {artist} - {title}")

            try:
                subprocess.run(base_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Downloaded: {artist} - {title}")
            except subprocess.CalledProcessError:
                print(f"Failed: {artist} - {title}")
        else:
            print(f"Failed: {artist} - {title}")


def fetch_liked_songs(sp):

    results = []
    offset = 0

    while True:

        items = sp.current_user_saved_tracks(limit=50, offset=offset)

        if not items["items"]:
            break

        for item in items["items"]:

            track = item["track"]
            artist = track["artists"][0]["name"]
            title = track["name"]

            results.append((artist, title))

        offset += 50

    return results


def main():

    print("\nSyncing Spotify liked songs...\n")

    sp = get_spotify_client()

    browser = detect_browser()

    if browser:
        print(f"Using browser cookies: {browser}")
    else:
        print("No supported browser detected. Continuing without cookies.")

    songs = fetch_liked_songs(sp)

    print(f"Found {len(songs)} liked songs\n")

    for artist, title in songs:
        download_song(artist, title, browser)

    print("\nDownload complete.\n")


if __name__ == "__main__":
    main()