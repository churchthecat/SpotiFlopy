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
        status TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ✅ safe migration
    try:
        conn.execute("ALTER TABLE tracks ADD COLUMN status TEXT")
        print("[DB] Added missing column: status")
    except Exception as e:
        if "duplicate column name" not in str(e):
            print("[DB ERROR]", e)

    return conn


def get_track(track_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT file, url, fingerprint, status
        FROM tracks
        WHERE track_id=?
    """, (track_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "file": row[0],
        "url": row[1],
        "fingerprint": row[2],
        "status": row[3],
    }


def upsert_track(track_id, file=None, url=None, fingerprint=None, status=None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tracks (track_id, file, url, fingerprint, status)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(track_id) DO UPDATE SET
        file=COALESCE(excluded.file, file),
        url=COALESCE(excluded.url, url),
        fingerprint=COALESCE(excluded.fingerprint, fingerprint),
        status=COALESCE(excluded.status, status),
        updated_at=CURRENT_TIMESTAMP
    """, (track_id, file, url, fingerprint, status))

    conn.commit()
    conn.close()
