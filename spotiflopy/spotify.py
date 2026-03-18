import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CONFIG_PATH = os.path.expanduser("~/.spotiflopy_config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise RuntimeError("Missing config. Run 'spotiflopy init'")
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_spotify():
    config = load_config()

    client_id = config.get("spotify_client_id")
    client_secret = config.get("spotify_client_secret")
    redirect_uri = config.get("spotify_redirect_uri")
    proxy = config.get("proxy")

    if not all([client_id, client_secret, redirect_uri]):
        raise RuntimeError("Incomplete config. Run 'spotiflopy init'")

    # Apply proxy if set
    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read playlist-read-private",
            cache_path=".spotiflopy_cache",
        )
    )


def get_tracks(limit=50, all_tracks=True):
    sp = get_spotify()

    results = []
    offset = 0

    while True:
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = response.get("items", [])

        if not items:
            break

        for item in items:
            t = item.get("track")

            # Skip invalid entries
            if not t:
                continue

            album = t.get("album", {})
            artists = t.get("artists", [])

            # --- Extract clean fields ---
            title = t.get("name")
            artist = ", ".join(a.get("name") for a in artists if a.get("name"))
            album_name = album.get("name")
            album_artist = ", ".join(
                a.get("name") for a in album.get("artists", []) if a.get("name")
            ) or artist

            release_date = album.get("release_date", "")
            year = release_date[:4] if release_date else ""

            images = album.get("images", [])
            cover_url = images[0].get("url") if images else None

            results.append({
                "title": title,
                "artist": artist,
                "album": album_name,
                "album_artist": album_artist,
                "spotify_id": t.get("id"),
                "track_number": t.get("track_number"),
                "disc_number": t.get("disc_number"),
                "duration_ms": t.get("duration_ms"),
                "year": year,
                "cover_url": cover_url,
            })

        if not all_tracks:
            break

        offset += limit

    return results
