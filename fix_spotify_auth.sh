#!/usr/bin/env bash
set -e

cat <<'PY' > spotiflopy/spotify.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import load_config


SCOPE = "user-library-read playlist-read-private playlist-read-collaborative"


def get_client():
    cfg = load_config()

    client_id = cfg.get("client_id")
    client_secret = cfg.get("client_secret")
    redirect_uri = cfg.get("redirect_uri")

    if not client_id or not client_secret:
        raise ValueError("Missing Spotify credentials in config. Run: spotiflopy init")

    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        open_browser=True,
        cache_path=None  # avoid weird cache issues
    )

    return spotipy.Spotify(auth_manager=auth)


def get_liked_tracks(since=None):
    sp = get_client()

    results = []
    offset = 0

    while True:
        res = sp.current_user_saved_tracks(limit=50, offset=offset)

        items = res.get("items", [])
        if not items:
            break

        for item in items:
            t = item["track"]

            results.append({
                "artist": t["artists"][0]["name"],
                "title": t["name"],
                "album": t["album"]["name"],
                "track_number": t["track_number"],
                "cover_url": t["album"]["images"][0]["url"] if t["album"]["images"] else None
            })

        offset += 50

    return results


def get_playlists():
    sp = get_client()
    res = sp.current_user_playlists(limit=50)

    return [
        {"name": p["name"], "id": p["id"]}
        for p in res.get("items", [])
    ]


def get_playlist_tracks(playlist_id, since=None):
    sp = get_client()

    results = []
    offset = 0

    while True:
        res = sp.playlist_items(playlist_id, limit=100, offset=offset)

        items = res.get("items", [])
        if not items:
            break

        for item in items:
            t = item.get("track")
            if not t:
                continue

            results.append({
                "artist": t["artists"][0]["name"],
                "title": t["name"],
                "album": t["album"]["name"],
                "track_number": t["track_number"],
                "cover_url": t["album"]["images"][0]["url"] if t["album"]["images"] else None
            })

        offset += 100

    return results
PY

pip install -e .

echo "Spotify auth fixed."
