import os

def verify(track, filepath):
    """
    Returns:
        (True, fingerprint)  -> match
        (False, None)        -> mismatch
        (None, None)         -> skipped (no key / error)
    """

    from spotiflopy.config import load_config

    config = load_config()
    api_key = os.environ.get("ACOUSTID_API_KEY") or config.get("acoustid_api_key")

    if not api_key:
        print("[ACOUSTID] Missing API key")
        return None, None

    try:
        import acoustid

        duration, fingerprint = acoustid.fingerprint_file(filepath)
        results = acoustid.lookup(api_key, fingerprint, duration)

        track_title = (track.get("title") or "").lower()

        for result in results.get("results", []):
            for rec in result.get("recordings", []):
                title = (rec.get("title") or "").lower()

                if track_title and track_title in title:
                    return True, fingerprint

        return False, None

    except Exception as e:
        print(f"[ACOUSTID ERROR] {e}")
        return None, None
