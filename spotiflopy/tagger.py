from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests
import os


def tag_file(path, track):
    try:
        audio = EasyID3(path)
    except:
        audio = EasyID3()
        audio.save(path)
        audio = EasyID3(path)

    audio["title"] = track["title"]
    audio["artist"] = track["artist"]

    if track.get("album"):
        audio["album"] = track["album"]

    if track.get("track_number"):
        audio["tracknumber"] = str(track["track_number"])

    audio.save()


def embed_cover(path, url):
    try:
        data = requests.get(url, timeout=10).content

        audio = ID3(path)
        audio["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=data
        )
        audio.save()

    except Exception:
        pass
