import click
from spotiflopy.repair import repair_track
from spotiflopy.library import get_all_tracks


@click.group()
def cli():
    pass


@cli.command()
def sync():
    tracks = get_all_tracks()

    print(f"🎧 Syncing {len(tracks)} tracks")

    for track in tracks:
        title = track.get("title", "UNKNOWN")

        # ✅ already good
        if track.get("status") == "ok":
            print(f"[SKIP] {title}")
            continue

        # 🔥 FORCE REPAIR FOR EVERYTHING ELSE
        print(f"[FORCE] {title}")

        try:
            success = repair_track(track)
        except Exception as e:
            print(f"[ERROR] {title} -> {e}")
            continue

        if success:
            print(f"[FIXED] {title}")
        else:
            print(f"[FAILED] {title}")

    print("✅ Sync complete")


if __name__ == "__main__":
    cli()
