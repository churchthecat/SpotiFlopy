import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotiflopy.config import load_config


def get_spotify():
    from spotiflopy.config import load_config
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth

    config = load_config()

    redirect_uri = config.get(
        "redirect_uri",
        "http://localhost:8888/callback"
    )

    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=config["spotify_client_id"],
        client_secret=config["spotify_client_secret"],
        redirect_uri=redirect_uri,
        scope="user-library-read playlist-read-private",
        cache_path=".spotiflopy_cache",
        open_browser=True
    ))


def parse_track(item):
    track = item.get("track") if "track" in item else item

    return {
        "artist": track["artists"][0]["name"],
        "title": track["name"],
        "album": track["album"]["name"],
        "track_number": track["track_number"],
        "duration_ms": track.get("duration_ms", 0),
    }


def get_tracks(all_tracks=False):
    sp = get_spotify()

    results = []
    limit = 50
    offset = 0

    print("🎵 Fetching Spotify tracks...")

    while True:
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)

        items = response.get("items", [])
        if not items:
            break

        for item in items:
            results.append(parse_track(item))

        print(f"[FETCHED] {len(results)} tracks")

        if not all_tracks:
            break  # only first page unless --full

        offset += limit

    print(f"✅ Total tracks: {len(results)}")
    return results
