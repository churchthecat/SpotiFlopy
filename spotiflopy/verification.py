import os
import acoustid

ACOUSTID_KEY = os.getenv("ACOUSTID_API_KEY")


# -----------------------------
# FINGERPRINT
# -----------------------------
def fingerprint_file(path):
    try:
        duration, fp = acoustid.fingerprint_file(path)
        return duration, fp
    except Exception:
        return None, None


# -----------------------------
# LOOKUP
# -----------------------------
def lookup_acoustid(path):
    if not ACOUSTID_KEY:
        return None

    try:
        results = acoustid.match(ACOUSTID_KEY, path)

        best = None
        best_score = 0

        for score, rid, title, artist in results:
            if score > best_score:
                best_score = score
                best = {
                    "score": score,
                    "title": title,
                    "artist": artist
                }

        return best

    except Exception:
        return None


# -----------------------------
# VERIFY MATCH
# -----------------------------
def verify_audio(path, track):
    result = lookup_acoustid(path)

    if not result:
        return 0.0

    score = result["score"]

    expected_title = (track.get("title") or "").lower()
    expected_artist = (track.get("artist") or "").lower()

    found_title = (result.get("title") or "").lower()
    found_artist = (result.get("artist") or "").lower()

    meta_score = 0

    if expected_title and expected_title in found_title:
        meta_score += 0.5

    if expected_artist and expected_artist in found_artist:
        meta_score += 0.5

    final_score = score * 0.7 + meta_score * 0.3

    return final_score
