import re


def normalize(text):
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)  # remove (official video) etc
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def verify_match(track, result):
    """
    track: dict with artist/title
    result: STRING (youtube title)
    """

    artist = normalize(track.get("artist", ""))
    title = normalize(track.get("title", ""))

    # ✅ result is now always treated as string
    result_title = normalize(result)

    score = 0

    # artist match
    if artist in result_title:
        score += 0.5

    # title match
    if title in result_title:
        score += 0.5

    # bonus: strong prefix match
    if result_title.startswith(f"{artist} {title}"):
        score += 0.3

    return min(score, 1.0)
