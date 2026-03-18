import os


def find_existing_versions(folder, title):
    mp3 = None
    flac = None

    for f in os.listdir(folder):
        if title in f:
            if f.endswith(".mp3"):
                mp3 = os.path.join(folder, f)
            elif f.endswith(".flac"):
                flac = os.path.join(folder, f)

    return mp3, flac


def should_upgrade(mp3, flac, target_format):
    if target_format != "flac":
        return False

    if flac:
        return False  # already best

    if mp3:
        return True

    return False


def replace_file(old_path, new_path):
    try:
        os.remove(old_path)
    except Exception:
        pass
