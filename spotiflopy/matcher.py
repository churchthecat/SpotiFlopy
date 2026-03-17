import os

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum() or c.isspace()).strip()


def build_index(base_dir):
    index = {}

    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.endswith(".mp3"):
                continue

            key = normalize(f)
            index[key] = os.path.join(root, f)

    return index


def find_in_index(index, track):
    query = normalize(f"{track['artist']} {track['title']}")

    # exact-ish lookup
    for k, path in index.items():
        if query in k:
            return path

    return None
