import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .config import load_config


def get_client():
    cfg = load_config()

    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=cfg.get("client_id"),
        client_secret=cfg.get("client_secret"),
        redirect_uri=cfg.get("redirect_uri"),
        scope="user-library-read playlist-read-private"
    ))


def get_liked_tracks(limit=None):
    sp = get_client()

    results = []
    offset = 0

    while True:
        batch = sp.current_user_saved_tracks(limit=50, offset=offset)

        items = batch.get("items", [])
        if not items:
            break

        for item in items:
            t = item["track"]

            results.append({
                "id": t["id"],
                "artist": ", ".join(a["name"] for a in t["artists"]),
                "title": t["name"],
                "album": t["album"]["name"],
                "track_number": t["track_number"],
                "duration_ms": t["duration_ms"],
            })

        offset += 50

        if limit and len(results) >= limit:
            return results[:limit]

    return results
