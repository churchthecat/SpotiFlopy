import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .spotify import get_liked_tracks
from .downloader import download
from .config import get_music_dir
from .library import repair_library


def sync(limit=None, workers=4):
    tracks = get_liked_tracks()

    if limit:
        tracks = tracks[:limit]

    music_dir = get_music_dir()

    print(f"Starting sync: {len(tracks)} tracks | {workers} workers")

    failed = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(download, t, music_dir): t for t in tracks
        }

        for future in as_completed(futures):
            track = futures[future]
            try:
                result = future.result()
                if result is False:
                    failed.append(track)
            except Exception as e:
                print(f"❌ Error: {e}")
                failed.append(track)

    # Retry pass
    if failed:
        print(f"\n🔁 Retrying {len(failed)} failed downloads...\n")

        for t in failed:
            try:
                download(t, music_dir)
            except Exception as e:
                print(f"❌ Final failure: {t['artist']} - {t['title']} ({e})")


def main():
    parser = argparse.ArgumentParser(prog="spotiflopy")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--limit", type=int)
    sync_parser.add_argument("--workers", type=int, default=4)

    subparsers.add_parser("repair")

    args = parser.parse_args()

    if args.command == "sync":
        sync(limit=args.limit, workers=args.workers)

    elif args.command == "repair":
        repair_library(get_music_dir())

    elif args.command == "init":
        print("Init handled via config file")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
