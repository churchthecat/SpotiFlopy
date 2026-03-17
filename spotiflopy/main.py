import argparse
from .spotify import get_liked_tracks
from .downloader import download


def sync():
    tracks = get_liked_tracks()
    for track in tracks:
        download(track)


def main():
    parser = argparse.ArgumentParser(
        prog="spotiflopy",
        description="Mirror your Spotify liked songs locally"
    )

    subparsers = parser.add_subparsers(dest="command")

    # sync command
    subparsers.add_parser("sync", help="Download liked songs")

    # playlist command (placeholder)
    subparsers.add_parser("playlist", help="Download a playlist")

    args = parser.parse_args()

    if args.command == "sync":
        sync()
    elif args.command == "playlist":
        print("Playlist support coming soon")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
