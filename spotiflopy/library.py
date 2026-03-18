import os
import re

def clean_album_name(name: str) -> str:
    patterns = [
        r"\(.*?edition.*?\)",
        r"\(.*?remaster.*?\)",
        r"\(.*?deluxe.*?\)",
        r"\(.*?bonus.*?\)",
        r"\(.*?expanded.*?\)",
        r"\(.*?anniversary.*?\)",
    ]

    cleaned = name
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def sanitize(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', text)


def get_track_path(base_dir, artist, album, track_number, title):
    artist = sanitize(artist)
    album = sanitize(clean_album_name(album))
    title = sanitize(title)

    artist_dir = os.path.join(base_dir, artist)
    album_dir = os.path.join(artist_dir, album)

    os.makedirs(album_dir, exist_ok=True)

    filename = f"{track_number:02d} - {title}.mp3"
    return os.path.join(album_dir, filename)


def repair_library(base_dir):
    print("Repairing library structure...")

    for artist in os.listdir(base_dir):
        artist_path = os.path.join(base_dir, artist)
        if not os.path.isdir(artist_path):
            continue

        for album in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album)
            if not os.path.isdir(album_path):
                continue

            cleaned_album = clean_album_name(album)

            if cleaned_album != album:
                new_album_path = os.path.join(artist_path, cleaned_album)

                if not os.path.exists(new_album_path):
                    print(f"Renaming album: {album} -> {cleaned_album}")
                    os.rename(album_path, new_album_path)
                else:
                    # Merge folders
                    print(f"Merging album folders: {album} -> {cleaned_album}")
                    for f in os.listdir(album_path):
                        src = os.path.join(album_path, f)
                        dst = os.path.join(new_album_path, f)
                        if not os.path.exists(dst):
                            os.rename(src, dst)
                    os.rmdir(album_path)

    print("Library repair complete.")
