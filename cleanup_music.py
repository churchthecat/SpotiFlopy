#!/usr/bin/env python3
import os
import re
from pathlib import Path

music_dir = Path.home() / "Music"

print("Cleaning music library...\n")


def normalize(text):
    text = text.lower()
    text = re.sub(r"\d+\s*-\s*", "", text)  # remove track numbers
    text = re.sub(r"[^\w\s]", "", text)     # remove punctuation
    return " ".join(text.split())


def ensure_track_format(file_path):
    name = file_path.stem

    # already formatted
    if re.match(r"^\d{2} - ", name):
        return

    # try to extract title
    clean_title = re.sub(r"^\d+\s*-\s*", "", name)

    new_name = f"01 - {clean_title}{file_path.suffix}"
    new_path = file_path.with_name(new_name)

    print("Renaming:", file_path, "→", new_path)
    file_path.rename(new_path)


for artist_path in music_dir.iterdir():
    if not artist_path.is_dir():
        continue

    # --- handle loose files ---
    singles_dir = artist_path / "Singles"
    singles_dir.mkdir(exist_ok=True)

    for item in list(artist_path.iterdir()):
        if item.is_file():

            if item.suffix == ".webm":
                print("Removing leftover:", item)
                item.unlink()
                continue

            if item.suffix == ".mp3":
                target = singles_dir / item.name
                print("Moving loose track → Singles:", item)
                item.rename(target)

    # --- deduplicate inside albums ---
    seen = {}

    for root, _, files in os.walk(artist_path):
        for f in files:
            if not f.endswith(".mp3"):
                continue

            full_path = Path(root) / f
            norm = normalize(f)

            if norm in seen:
                print("Removing duplicate:", full_path)
                full_path.unlink()
            else:
                seen[norm] = full_path

    # --- enforce track naming ---
    for root, _, files in os.walk(artist_path):
        for f in files:
            if f.endswith(".mp3"):
                ensure_track_format(Path(root) / f)


# --- remove empty folders ---
for root, dirs, files in os.walk(music_dir, topdown=False):
    if not dirs and not files:
        print("Removing empty folder:", root)
        os.rmdir(root)


print("\nLibrary cleanup complete.")
