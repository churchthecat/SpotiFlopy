from spotiflopy.db import get_all_tracks, update_track
from spotiflopy.repair import repair_track


def sync_tracks(limit=None):
    tracks = get_all_tracks()

    if limit:
        tracks = tracks[:limit]

    print(f"🎧 Syncing {len(tracks)} tracks")

    for track in tracks:
        title = track.get("title")
        artist = track.get("artist")

        if not title or not artist:
            print(f"[SKIP INVALID] {track}")
            continue

        if track.get("status") == "ok" and track.get("file"):
            print(f"[SKIP] {artist} - {title}")
            continue

        print(f"[PROCESS] {artist} - {title}")

        try:
            success = repair_track(track)
        except Exception as e:
            print(f"[ERROR] {artist} - {title} -> {e}")
            continue

        if success:
            print(f"[OK] {artist} - {title}")
            update_track(track, status="ok")
        else:
            print(f"[FAILED] {artist} - {title}")
            update_track(track, status="failed")

    print("✅ Sync complete")


# 🔥 FIXED SIGNATURE (matches CLI)
def repair_library(full=False, fs=False):
    tracks = get_all_tracks()

    print(f"🔧 Repairing {len(tracks)} tracks")

    for track in tracks:
        title = track.get("title")
        artist = track.get("artist")

        if not title or not artist:
            continue

        # skip already good unless full repair requested
        if not full and track.get("status") == "ok":
            continue

        print(f"[REPAIR] {artist} - {title}")

        try:
            success = repair_track(track)
        except Exception as e:
            print(f"[ERROR] {artist} - {title} -> {e}")
            continue

        if success:
            update_track(track, status="ok")
            print(f"[FIXED] {artist} - {title}")
        else:
            update_track(track, status="failed")
            print(f"[FAILED] {artist} - {title}")
