import re
import shutil
from pathlib import Path
from collections import defaultdict

from .config import get_music_dir


BAD_WORDS = [
    "official video",
    "official hd video",
    "lyrics",
    "audio",
    "topic",
    "live"
]


def clean_title(title):

    t = title.lower()

    for word in BAD_WORDS:
        t = t.replace(word, "")

    t = re.sub(r"\(.*?\)", "", t)
    t = re.sub(r"\[.*?\]", "", t)

    t = t.replace("_", " ")
    t = re.sub(r"\s+", " ", t)

    return t.strip()


def repair_library():

    music_dir = get_music_dir()

    print("\nScanning library...\n")

    songs = defaultdict(list)

    for file in music_dir.rglob("*.mp3"):

        name = file.stem
        cleaned = clean_title(name)

        songs[cleaned].append(file)

    duplicates = 0

    for title, files in songs.items():

        if len(files) <= 1:
            continue

        files.sort(key=lambda f: len(f.name))

        keep = files[0]

        for f in files[1:]:

            print("Removing duplicate:", f)
            f.unlink()
            duplicates += 1

    print(f"\nRemoved {duplicates} duplicates")

    fix_filenames(music_dir)


def fix_filenames(music_dir):

    print("\nCleaning filenames...\n")

    for file in music_dir.rglob("*.mp3"):

        name = file.stem

        cleaned = clean_title(name)

        new_name = cleaned.title() + ".mp3"

        new_path = file.with_name(new_name)

        if new_path != file:

            try:
                file.rename(new_path)
                print("Renamed:", new_path.name)
            except:
                pass

    print("\nFilename cleanup complete.\n")