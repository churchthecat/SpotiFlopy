import requests
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC, TCON, APIC, TPE2, COMM
from mutagen.mp3 import MP3


def fetch_cover(url):
    if not url:
        return None
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


def tag_file(path, track):
    audio = MP3(path, ID3=ID3)

    try:
        audio.add_tags()
    except Exception:
        pass

    tags = audio.tags

    title = track.get("title", "")
    artist = track.get("artist", "")
    album = track.get("album", "")
    track_number = track.get("track_number", 0)
    cover_url = track.get("cover_url")
    spotify_id = track.get("spotify_id")

    # Optional fields (safe defaults)
    year = track.get("year", "")
    genre = track.get("genre", "")
    album_artist = track.get("album_artist", artist)

    # --- Core tags ---
    tags["TIT2"] = TIT2(encoding=3, text=title)
    tags["TPE1"] = TPE1(encoding=3, text=artist)
    tags["TALB"] = TALB(encoding=3, text=album)
    tags["TPE2"] = TPE2(encoding=3, text=album_artist)
    tags["TRCK"] = TRCK(encoding=3, text=str(track_number))

    # --- Optional tags ---
    if year:
        tags["TDRC"] = TDRC(encoding=3, text=str(year))

    if genre:
        tags["TCON"] = TCON(encoding=3, text=genre)

    if spotify_id:
        tags["COMM"] = COMM(
            encoding=3,
            lang="eng",
            desc="Spotify",
            text=f"https://open.spotify.com/track/{spotify_id}"
        )

    # --- Cover art ---
    cover_data = fetch_cover(cover_url)
    if cover_data:
        tags["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=cover_data
        )
        print("[COVER] Embedded")

    audio.save()
    print(f"[TAGGED] {path}")
