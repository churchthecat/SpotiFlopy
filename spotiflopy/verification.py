from mutagen.mp3 import MP3


def verify_audio(file_path, track):
    """
    Returns score between 0.0 and 1.0
    """

    try:
        audio = MP3(file_path)
    except Exception as e:
        print("[VERIFY ERROR]", e)
        return 0.0

    score = 0.0

    # -----------------------------
    # 1. Duration check (STRONG)
    # -----------------------------
    expected = track.get("duration_ms")
    if expected:
        expected_sec = expected / 1000
        actual_sec = audio.info.length

        diff = abs(actual_sec - expected_sec)

        if diff < 2:
            score += 0.5
        elif diff < 5:
            score += 0.3
        elif diff < 10:
            score += 0.1
        else:
            print(f"[VERIFY] duration mismatch: {actual_sec:.1f}s vs {expected_sec:.1f}s")

    # -----------------------------
    # 2. Bitrate check
    # -----------------------------
    bitrate = audio.info.bitrate / 1000  # kbps

    if bitrate >= 256:
        score += 0.3
    elif bitrate >= 192:
        score += 0.2
    elif bitrate >= 128:
        score += 0.1
    else:
        print(f"[VERIFY] low bitrate: {bitrate}kbps")

    # -----------------------------
    # 3. File size sanity (weak)
    # -----------------------------
    import os
    size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if size_mb > 3:
        score += 0.1

    # -----------------------------
    # clamp
    # -----------------------------
    return min(score, 1.0)
