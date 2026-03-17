import os
from .fingerprint import get_fingerprint, load_cache, save_cache

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum() or c.isspace()).strip()


def build_index(base_dir):
    index = {}
    files = []

    for root, _, fs in os.walk(base_dir):
        for f in fs:
            if not f.endswith(".mp3"):
                continue
            path = os.path.join(root, f)
            files.append(path)

            key = normalize(f)
            index[key] = path

    return index, files


def find_in_index(index_data, track):
    index, files = index_data

    query = normalize(f"{track['artist']} {track['title']}")

    # --- fast filename match ---
    for k, path in index.items():
        if query in k:
            return path

    # --- fingerprint fallback ---
    cache = load_cache()

    for path in files:
        fp = get_fingerprint(path, cache)
        if not fp:
            continue

        # crude similarity (fast compare)
        if query[:10] in fp:
            save_cache(cache)
            return path

    save_cache(cache)
    return None
