import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import load_config


def get_client():
    cfg = load_config()

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=cfg["client_id"],
            client_secret=cfg["client_secret"],
            redirect_uri="http://localhost:8888/callback",
            scope="user-library-read"
        )
    )


def get_liked_tracks():
    sp = get_client()

    results = []
    offset = 0

    while True:
        data = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = data.get("items", [])

        if not items:
            break

        for item in items:
            track = item["track"]
            results.append({
                "artist": track["artists"][0]["name"],
                "title": track["name"]
            })

        offset += 50

    return results
