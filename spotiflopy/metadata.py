import requests
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error


def tag_file(filepath, track):
    try:
        # ✅ Ensure ID3 exists
        try:
            audio = MP3(filepath, ID3=EasyID3)
        except error:
            audio = MP3(filepath)
            audio.add_tags()

        audio["title"] = track.get("title", "")
        audio["artist"] = track.get("artist", "")
        audio["album"] = track.get("album", "")

        if track.get("track_number"):
            audio["tracknumber"] = str(track["track_number"])

        audio.save()

        # 🔥 Add album art
        image_url = track.get("cover_url")

        if image_url:
            add_cover_art(filepath, image_url)
        else:
            print("[COVER] No cover URL")

        print(f"[TAGGED] {filepath}")

    except Exception as e:
        print(f"[TAG ERROR] {e}")


def add_cover_art(filepath, image_url):
    try:
        img_data = requests.get(image_url, timeout=10).content

        audio = MP3(filepath, ID3=ID3)

        # ✅ FORCE tag creation if missing
        if audio.tags is None:
            audio.add_tags()

        # ✅ Remove old cover (avoid duplicates)
        audio.tags.delall("APIC")

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
