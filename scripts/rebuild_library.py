import json
import os

with open("full_library.json") as f:
    data = json.load(f)

tracks = []
seen = set()

for t in data:
    key = (t["artist"], t["title"])
    if key in seen:
        continue
    seen.add(key)

    tracks.append({
        "artist": t["artist"],
        "title": t["title"],
        "album": t.get("album") or "Unknown",
        "track_number": t.get("track_number"),
        "year": t.get("year"),
        "cover_url": t.get("cover_url"),
        "youtube_url": t.get("youtube_url"),
        "file": t.get("file"),
        "status": t.get("status") or "unknown"
    })

out = os.path.expanduser("~/.spotiflopy_library.json")

with open(out, "w") as f:
    json.dump({"tracks": tracks}, f, indent=2)

print(f"Rebuilt FULL library with {len(tracks)} tracks")
