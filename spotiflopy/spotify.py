import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-library-read playlist-read-private"
))


def parse_track(item):
    t = item["track"]

    if not t:
        return None

    return {
        "id": t["id"],
        "title": t["name"],
        "artist": t["artists"][0]["name"],
        "album": t["album"]["name"],
        "track_number": t["track_number"],
        "art": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
    }


def get_liked_tracks():
    results = []
    offset = 0

    while True:
        res = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = res["items"]

        if not items:
            break

        for i in items:
            t = parse_track(i)
            if t:
                results.append(t)

        offset += 50

    return results


def get_playlists():
    results = []
    res = sp.current_user_playlists()

    for p in res["items"]:
        results.append({"id": p["id"], "name": p["name"]})

    return results


def get_playlist_tracks(pid):
    results = []
    offset = 0

    while True:
        res = sp.playlist_items(pid, limit=100, offset=offset)
        items = res["items"]

        if not items:
            break

        for i in items:
            t = parse_track(i)
            if t:
                results.append(t)

        offset += 100

    return results
