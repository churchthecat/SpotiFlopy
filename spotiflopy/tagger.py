from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests


def tag_file(path, track):
    """
    Authoritative metadata writer.
    Safe to call multiple times.
    """

    try:
        audio = EasyID3(path)
    except:
        audio = EasyID3()
        audio.save(path)
        audio = EasyID3(path)

    if track.get("title"):
        audio["title"] = track["title"]

    if track.get("artist"):
        audio["artist"] = track["artist"]

    if track.get("album"):
        audio["album"] = track["album"]

    if track.get("track_number"):
        audio["tracknumber"] = str(track["track_number"])

    if track.get("year"):
        audio["date"] = str(track["year"])

    audio.save()

    # embed cover AFTER saving tags
    if track.get("cover_url"):
        embed_cover(path, track["cover_url"])


def embed_cover(path, url):
    try:
        data = requests.get(url, timeout=10).content

        audio = ID3(path)

        audio.delall("APIC")  # prevent duplicates

        audio.add(APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=data
        ))

        audio.save()

        print(f"[COVER] Embedded")

    except Exception as e:
        print(f"[COVER FAIL] {e}")
