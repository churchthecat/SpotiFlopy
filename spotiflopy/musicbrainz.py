import musicbrainzngs

musicbrainzngs.set_useragent("spotiflopy", "1.0", "https://github.com")


def enrich_metadata(artist, title):
    try:
        result = musicbrainzngs.search_recordings(
            recording=title,
            artist=artist,
            limit=1
        )

        recs = result.get("recording-list", [])
        if not recs:
            return None

        r = recs[0]

        return {
            "title": r.get("title"),
            "artist": r["artist-credit"][0]["artist"]["name"],
            "album": r.get("release-list", [{}])[0].get("title"),
            "year": r.get("first-release-date", "")[:4],
        }

    except Exception:
        return None
