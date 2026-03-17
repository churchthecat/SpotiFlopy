import re

def normalize(s):
    if not s:
        return ""

    s = s.lower()

    # remove punctuation
    s = re.sub(r"[^\w\s]", " ", s)

    # remove common junk words
    junk = [
        "lyrics", "lyric", "official", "video",
        "audio", "hd", "4k", "remaster", "remastered",
        "live", "version", "explicit"
    ]

    for j in junk:
        s = s.replace(j, "")

    # collapse spaces
    s = re.sub(r"\s+", " ", s).strip()

    return s


def verify_audio(track, candidate):
    t_artist = normalize(track.get("artist"))
    t_title = normalize(track.get("title"))

    c_title = normalize(candidate.get("title"))

    score = 0.0

    # strong title match
    if t_title in c_title:
        score += 0.6

    # artist match
    if t_artist and t_artist.split()[0] in c_title:
        score += 0.3

    # fallback fuzzy-ish
    overlap = sum(1 for w in t_title.split() if w in c_title)
    if overlap:
        score += min(0.3, overlap * 0.1)

    return min(score, 1.0)
