import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import load_config


def get_client():
    cfg = load_config()

    # Support both formats
    if "spotify" in cfg:
        spcfg = cfg["spotify"]
        client_id = spcfg.get("client_id")
        client_secret = spcfg.get("client_secret")
    else:
        client_id = cfg.get("client_id")
        client_secret = cfg.get("client_secret")

    if not client_id or not client_secret:
        raise Exception("Missing Spotify credentials")

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8888/callback",
            scope="user-library-read"
        )
    )


def get_liked_tracks():
    sp = get_client()
    results = sp.current_user_saved_tracks(limit=50)

    tracks = []
    for item in results["items"]:
        track = item["track"]
        tracks.append({
            "artist": track["artists"][0]["name"],
            "track": track["name"],
            "album": track["album"]["name"]
        })

    return tracks
