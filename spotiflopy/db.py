import sqlite3
import os

DB_FILE = ".spotiflopy.db"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        track_id TEXT PRIMARY KEY,
        file TEXT,
        url TEXT,
        fingerprint TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    return conn


def get_track(track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT file, url, fingerprint FROM tracks WHERE track_id=?", (track_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "file": row[0],
        "url": row[1],
        "fingerprint": row[2],
    }


def upsert_track(track_id, file=None, url=None, fingerprint=None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tracks (track_id, file, url, fingerprint)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(track_id) DO UPDATE SET
        file=COALESCE(excluded.file, file),
        url=COALESCE(excluded.url, url),
        fingerprint=COALESCE(excluded.fingerprint, fingerprint),
        updated_at=CURRENT_TIMESTAMP
    """, (track_id, file, url, fingerprint))

    conn.commit()
    conn.close()
