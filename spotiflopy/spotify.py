import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import load_config


def get_client():
    cfg = load_config()

    # ✅ Support BOTH formats
    if "spotify" in cfg:
        spcfg = cfg["spotify"]
    else:
        spcfg = cfg

    client_id = spcfg.get("client_id")
    client_secret = spcfg.get("client_secret")

    if not client_id or not client_secret:
        raise ValueError("Missing Spotify credentials in config")

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-library-read",
            cache_path=".spotiflopy_token_cache",
        )
    )


def get_liked_tracks():
    sp = get_client()

    results = sp.current_user_saved_tracks(limit=50)

    tracks = []

    for item in results["items"]:
        t = item["track"]

        tracks.append({
            "artist": t["artists"][0]["name"],
            "title": t["name"],
            "album": t["album"]["name"],
            "track_number": t["track_number"],
        })

    return tracks
