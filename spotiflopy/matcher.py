def build_query(track):

    artist = track["artist"]
    title = track["title"]

    return f"{artist} - {title} audio"