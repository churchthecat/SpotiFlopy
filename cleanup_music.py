#!/usr/bin/env python3
import os

music_dir = os.path.expanduser("~/Music")

print("Cleaning music library...\n")

for artist in os.listdir(music_dir):
    artist_path = os.path.join(music_dir, artist)

    if not os.path.isdir(artist_path):
        continue

    for item in os.listdir(artist_path):
        item_path = os.path.join(artist_path, item)

        if item.endswith(".webm"):
            print("Removing leftover:", item_path)
            os.remove(item_path)
            continue

        if item.endswith(".mp3"):
            title = item[:-4].lower()
            found_album_version = False

            for album in os.listdir(artist_path):
                album_path = os.path.join(artist_path, album)

                if not os.path.isdir(album_path):
                    continue

                for f in os.listdir(album_path):
                    if f.endswith(".mp3") and title in f.lower():
                        found_album_version = True
                        break

                if found_album_version:
                    break

            if found_album_version:
                print("Removing duplicate:", item_path)
                os.remove(item_path)

for root, dirs, files in os.walk(music_dir, topdown=False):
    if not dirs and not files:
        print("Removing empty folder:", root)
        os.rmdir(root)

print("\nLibrary cleanup complete.")
