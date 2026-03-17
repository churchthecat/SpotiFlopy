import json
import subprocess


def normalize(s):
    return s.lower().replace("&", "and")


def search_youtube(query, limit=5):
    cmd = [
        "yt-dlp",
        f"ytsearch{limit}:{query}",
        "--dump-json",
        "--skip-download",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    results = []
    for line in proc.stdout.splitlines():
        try:
            results.append(json.loads(line))
        except:
            pass

    return results


def score_result(video, track):
    score = 0

    title = normalize(video.get("title", ""))
    uploader = normalize(video.get("uploader", ""))

    artist = normalize(track["artist"])
    song = normalize(track["title"])

    if artist in title or artist in uploader:
        score += 40

    if song in title:
        score += 40

    duration = video.get("duration")
    if duration and track.get("duration"):
        if abs(duration - track["duration"]) < 5:
            score += 15

    if "official" in title:
        score += 5

    if "vevo" in uploader or "official" in uploader:
        score += 10

    return score


def best_match(track):
    query = f"{track['artist']} {track['title']}"

    results = search_youtube(query)

    best = None
    best_score = 0

    for r in results:
        s = score_result(r, track)

        if s > best_score:
            best_score = s
            best = r

    if best_score < 50:
        return None

    return best["webpage_url"]
