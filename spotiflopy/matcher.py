import os
from .fingerprint import get_fingerprint, load_cache, save_cache
from .acoustid import lookup_acoustid

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
            index[normalize(f)] = path

    return index, files


def match_acoustid(track, candidates):
    target_artist = normalize(track["artist"])
    target_title = normalize(track["title"])

    for path in candidates:
        results = lookup_acoustid(path)
        if not results:
            continue

        for artists, title in results:
            a = normalize(" ".join(artists))
            t = normalize(title)

            if target_title in t and target_artist in a:
                return path

    return None


def find_in_index(index_data, track):
    index, files = index_data

    query = normalize(f"{track['artist']} {track['title']}")

    # 1. fast filename match
    for k, path in index.items():
        if query in k:
            return path

    # 2. fingerprint cache match
    cache = load_cache()
    for path in files:
        fp = get_fingerprint(path, cache)
        if not fp:
            continue

        if query[:10] in fp:
            save_cache(cache)
            return path

    save_cache(cache)

    # 3. acoustid (slow but accurate)
    print("🧬 AcoustID matching...")
    match = match_acoustid(track, files)
    if match:
        return match

    return None
