import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

from .config import load_config


SCOPES = "user-library-read playlist-read-private"


def get_client():
    cfg = load_config()

    if not all(k in cfg for k in ["client_id", "client_secret", "redirect_uri"]):
        raise ValueError("Missing Spotify credentials in config")

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=cfg["client_id"],
            client_secret=cfg["client_secret"],
            redirect_uri=cfg["redirect_uri"],
            scope=SCOPES,
        )
    )


def parse_track(item):
    track = item["track"]

    return {
        "artist": track["artists"][0]["name"],
        "title": track["name"],
        "album": track["album"]["name"],
        "track_number": track["track_number"],
        "duration": track["duration_ms"] // 1000,
        "added_at": item.get("added_at"),
    }


def get_liked_tracks(since=None):
    sp = get_client()

    results = []
    offset = 0

    while True:
        res = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = res["items"]

        if not items:
            break

        for item in items:
            if since and item["added_at"] <= since:
                return results
            results.append(parse_track(item))

        offset += 50

    return results


def get_playlists():
    sp = get_client()
    playlists = []

    res = sp.current_user_playlists()
    for p in res["items"]:
        playlists.append({"name": p["name"], "id": p["id"]})

    return playlists


def get_playlist_tracks(playlist_id, since=None):
    sp = get_client()

    results = []
    offset = 0

    while True:
        res = sp.playlist_items(playlist_id, limit=100, offset=offset)
        items = res["items"]

        if not items:
            break

        for item in items:
            if not item["track"]:
                continue

            if since and item["added_at"] <= since:
                return results

            results.append(parse_track(item))

        offset += 100

    return results
