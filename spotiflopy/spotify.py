import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope="user-library-read"
    ))


# -----------------------------
# Extract full metadata
# -----------------------------
def parse_track(track):
    if not track:
        return None

    artists = track.get("artists", [])
    artist_names = ", ".join(a["name"] for a in artists if a.get("name"))

    album = track.get("album", {})
    images = album.get("images", [])

    cover_url = None
    if images:
        # highest resolution first
        cover_url = images[0].get("url")

    release_date = album.get("release_date", "")
    year = release_date[:4] if release_date else None

    return {
        "id": track.get("id"),
        "title": track.get("name"),
        "artist": artist_names,
        "album": album.get("name"),
        "track_number": track.get("track_number"),
        "year": year,
        "cover_url": cover_url
    }


# -----------------------------
# Get liked tracks (FULL METADATA)
# -----------------------------
def get_liked_tracks(limit=None):
    sp = get_client()

    results = []
    offset = 0
    page_size = 50

    while True:
        fetch_size = page_size

        if limit:
            remaining = limit - len(results)
            if remaining <= 0:
                break
            fetch_size = min(page_size, remaining)

        data = sp.current_user_saved_tracks(
            limit=fetch_size,
            offset=offset
        )

        items = data.get("items", [])
        if not items:
            break

        for item in items:
            track = item.get("track")
            parsed = parse_track(track)

            if parsed:
                results.append(parsed)

        offset += len(items)

    return results


# -----------------------------
# OPTIONAL: Get playlist tracks
# -----------------------------
def get_playlist_tracks(playlist_id, limit=None):
    sp = get_client()

    results = []
    offset = 0
    page_size = 100

    while True:
        fetch_size = page_size

        if limit:
            remaining = limit - len(results)
            if remaining <= 0:
                break
            fetch_size = min(page_size, remaining)

        data = sp.playlist_items(
            playlist_id,
            limit=fetch_size,
            offset=offset
        )

        items = data.get("items", [])
        if not items:
            break

        for item in items:
            track = item.get("track")
            parsed = parse_track(track)

            if parsed:
                results.append(parsed)

        offset += len(items)

    return results
