from mutagen.mp3 import MP3
import os


def verify_audio(file_path, track):
    try:
        audio = MP3(file_path)
    except:
        return 0.0

    score = 0.0

    # duration
    expected = track.get("duration_ms")
    if expected:
        diff = abs(audio.info.length - (expected / 1000))
        if diff < 2:
            score += 0.5
        elif diff < 5:
            score += 0.3

    # bitrate
    bitrate = audio.info.bitrate / 1000
    if bitrate >= 256:
        score += 0.3
    elif bitrate >= 192:
        score += 0.2

    # size sanity
    if os.path.getsize(file_path) > 3_000_000:
        score += 0.1

    return score
