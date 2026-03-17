import os
import subprocess
import shutil


def download(track, base_dir):
    artist = track["artist"]
    album = track.get("album") or "Unknown Album"
    title = track["title"]
    track_num = track.get("track_number", 0)

    safe_artist = artist.replace("/", "-")
    safe_album = album.replace("/", "-")
    safe_title = title.replace("/", "-")

    folder = os.path.join(base_dir, safe_artist, safe_album)
    os.makedirs(folder, exist_ok=True)

    filename = f"{track_num:02d} - {safe_title}.mp3"
    output_path = os.path.join(folder, filename)

    if os.path.exists(output_path):
        return output_path  # already exists

    query = f"{artist} - {title}"

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--extract-audio",
        "--audio-format", "mp3",
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails", "png",
        "-o", output_path,
        "--no-playlist",
        "--quiet"
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0 or not os.path.exists(output_path):
        print(f"⚠️ Download failed: {query}")
        return None

    return output_path
