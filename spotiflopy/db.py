import sqlite3
import os

DB_FILE = ".spotiflopy.db"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    conn.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        track_id TEXT PRIMARY KEY,
        file TEXT,
        url TEXT,
        fingerprint TEXT,
        confidence REAL,
        artist TEXT,
        title TEXT,
        acoustid TEXT,
        failed_attempts INTEGER DEFAULT 0,
        album TEXT,
        track_number INTEGER,
        year TEXT,
        cover_url TEXT,
        youtube_url TEXT,
        status TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    return conn


def get_all_tracks():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM tracks
        WHERE artist IS NOT NULL
          AND title IS NOT NULL
          AND artist != ''
          AND title != ''
    """)

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_track(track_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tracks WHERE track_id=?", (track_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row) if row else None


def upsert_track(track_id, **kwargs):
    conn = get_conn()
    cur = conn.cursor()

    fields = ["track_id"]
    values = [track_id]

    for k, v in kwargs.items():
        fields.append(k)
        values.append(v)

    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields)

    update_clause = ", ".join([
        f"{k}=COALESCE(excluded.{k}, {k})"
        for k in kwargs.keys()
    ]) + ", updated_at=CURRENT_TIMESTAMP"

    query = f"""
    INSERT INTO tracks ({columns})
    VALUES ({placeholders})
    ON CONFLICT(track_id) DO UPDATE SET
        {update_clause}
    """

    cur.execute(query, values)
    conn.commit()
    conn.close()


def update_track(track, **kwargs):
    conn = get_conn()
    cur = conn.cursor()

    fields = []
    values = []

    for k, v in kwargs.items():
        fields.append(f"{k}=?")
        values.append(v)

    values.append(track.get("title"))
    values.append(track.get("artist"))

    cur.execute(f"""
        UPDATE tracks
        SET {", ".join(fields)}, updated_at=CURRENT_TIMESTAMP
        WHERE title=? AND artist=?
    """, values)

    conn.commit()
    conn.close()
