import requests
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


def tag_file(filepath, track):
    try:
        audio = MP3(filepath, ID3=EasyID3)

        audio["title"] = track.get("title", "")
        audio["artist"] = track.get("artist", "")
        audio["album"] = track.get("album", "")

        if track.get("track_number"):
            audio["tracknumber"] = str(track["track_number"])

        audio.save()

        # 🔥 Add album art if available
        image_url = track.get("cover_url")

        if image_url:
            add_cover_art(filepath, image_url)

        print(f"[TAGGED] {filepath}")

    except Exception as e:
        print(f"[TAG ERROR] {e}")


def add_cover_art(filepath, image_url):
    try:
        img_data = requests.get(image_url, timeout=10).content

        audio = MP3(filepath, ID3=ID3)

        audio.tags.add(
            APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=img_data
            )
        )

        audio.save()

        print("[COVER] Embedded")

    except Exception as e:
        print(f"[COVER ERROR] {e}")
