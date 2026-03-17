import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .config import load_config


def get_client():

    cfg = load_config()
    spcfg = cfg["spotify"]

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spcfg["client_id"],
            client_secret=spcfg["client_secret"],
            redirect_uri=spcfg["redirect_uri"],
            scope="user-library-read"
        )
    )


def get_liked_tracks():

    sp = get_client()

    results = sp.current_user_saved_tracks(limit=50)

    tracks = []

    while results:

        for item in results["items"]:

            track = item["track"]

            tracks.append({
                "artist": track["artists"][0]["name"],
		"track": track["name"],
                "album": track["album"]["name"]
            })

        if results["next"]:
            results = sp.next(results)
        else:
            results = None

    return tracks