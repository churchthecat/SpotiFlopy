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
return spotipy.Spotify(
auth_manager=SpotifyOAuth(
scope="user-library-read",
cache_path=".spotiflopy_token_cache",
)
)

def load_config():
if CONFIG_FILE.exists():
with open(CONFIG_FILE) as f:
return json.load(f)

```
folder = input("Enter download folder (default: ~/Desktop/Songs): ").strip()

if not folder:
    folder = str(Path.home() / "Desktop" / "Songs")

config = {"download_folder": folder}

with open(CONFIG_FILE, "w") as f:
    json.dump(config, f)

return config
```

def load_downloaded():
downloaded = set()

```
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            downloaded.add((row["Artist"], row["Track"]))

return downloaded
```

def save_download(artist, album, track, track_number):
file_exists = os.path.exists(CSV_FILE)

```
with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    if not file_exists:
        writer.writerow(["Artist", "Album", "Track", "Track Number"])

    writer.writerow([artist, album, track, track_number])
```

def get_liked_songs(sp):
results = []
offset = 0

```
while True:
    data = sp.current_user_saved_tracks(limit=50, offset=offset)
    items = data["items"]

    if not items:
        break

    results.extend(items)
    offset += 50

return results
```

def sanitize(text):
return "".join(c for c in text if c not in '\/:*?"<>|').strip()

def download_track(track_data, base_folder, downloaded):
track = track_data["track"]

```
artist = sanitize(track["artists"][0]["name"])
album = sanitize(track["album"]["name"])
name = sanitize(track["name"])
track_number = track["track_number"]

if (artist, name) in downloaded:
    return

artist_dir = os.path.join(base_folder, artist)
album_dir = os.path.join(artist_dir, album)

os.makedirs(album_dir, exist_ok=True)

filename = f"{track_number:02d} - {name}.%(ext)s"
output_path = os.path.join(album_dir, filename)

search_query = f"{artist} {name} official audio"

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": output_path,
    "quiet": True,
    "noplaylist": True,
    "retries": 5,
    "fragment_retries": 5,
    "continuedl": True,
    "default_search": "ytsearch1",
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])

    save_download(artist, album, name, track_number)

    print(f"Downloaded: {artist} - {name}")

except Exception as e:
    print(f"Failed: {artist} - {name}")
    print(e)
```

def main():
config = load_config()
folder = config["download_folder"]

```
sp = get_spotify_client()

songs = get_liked_songs(sp)

downloaded = load_downloaded()

print(f"Found {len(songs)} liked songs")

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(
        lambda t: download_track(t, folder, downloaded),
        songs
    )
```

if **name** == "**main**":
main()
