import sys
from .spotify import get_liked_tracks
from .downloader import download
from .library import load_index, save_index, exists, add


def sync():

    print("\nFetching Spotify liked songs...\n")

    tracks = get_liked_tracks()

    index = load_index()

    for track in tracks:

        key = f"{track['artist']} - {track['track']}"

        if exists(index, key):
            print(f"Skipping (library): {key}")
            continue

        print(f"Downloading: {key}")

        try:
            download(track)
            add(index, key)

        except Exception as e:
            print(f"Failed: {e}")

    save_index(index)

    print("\nAll downloads finished.\n")


def main():

    if len(sys.argv) < 2:
        print("Usage: spotiflopy sync")
        return

    cmd = sys.argv[1]

    if cmd == "sync":
        sync()

    else:
        print("Unknown command")