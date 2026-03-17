# 🎧 SpotiFlopy

Spotify → local music sync tool.

Sync your Spotify liked songs and playlists into a clean, tagged, deduplicated local music library with smart matching, verification, caching, and fast incremental sync.

---

## ✨ Features

- Sync liked songs and playlists
- Smart YouTube matching (multi-pass + scoring)
- Pre-download scoring (avoids bad downloads)
- Duration + bitrate verification (high accuracy)
- YouTube URL caching (no repeated searches)
- Incremental sync (skip existing files)
- Clean Spotify metadata tagging
- Album artwork embedding
- Repair mode (re-tag + fix covers)
- SQLite database tracking
- Clean folder structure

---

## 🚀 Install

git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy

python3 -m venv myenv
source myenv/bin/activate

pip install -e .

---

## ⚙️ Setup

Run:

spotiflopy init

You will be prompted for:

- Spotify Client ID
- Spotify Client Secret
- Redirect URI

Default:

http://127.0.0.1:8888/callback

---

## 🔑 Spotify App Setup (Local)

Create an app:

https://developer.spotify.com/dashboard

Add redirect URI EXACTLY:

http://127.0.0.1:8888/callback

Run:

spotiflopy sync

---

## ☁️ Headless / Server Setup (Cloudflare Proxy)

### 1. Create public callback

Use Cloudflare Tunnel or reverse proxy:

https://your-domain.com/callback

### 2. Add to Spotify

Add in dashboard:

https://your-domain.com/callback

### 3. Init with:

spotiflopy init

Use:

https://your-domain.com/callback

### 4. Run:

spotiflopy sync

👉 Spotify → your domain → your local app

Example proxy:
https://github.com/1111ij1/spotify-proxy

---

## ▶️ Usage

Sync liked songs:

spotiflopy sync

Limit tracks:

spotiflopy sync --limit 10

Repair library:

spotiflopy repair

---

## 🧠 Matching Pipeline

1. YouTube search
2. Pre-score (title + artist + duration)
3. Download best candidates only
4. Verify audio:
   - Duration match
   - Bitrate quality
   - File size sanity
5. Accept only high-score matches (≥ 0.8)
6. Cache YouTube URL
7. Apply metadata + cover

---

## ⚡ Performance

- Cached tracks skip search entirely
- Only top candidates are downloaded
- Verification prevents bad files early

---

## 📁 Structure

Music/
  Artist/
    Album/
      01 - Track.mp3

---

## 🛠 Requirements

Python 3.10+  
ffmpeg  
yt-dlp  

Install:

sudo apt install ffmpeg yt-dlp

---

## ⚠️ Notes

- Spotify does NOT provide audio files
- Audio is sourced via yt-dlp
- Matching is best-effort but highly accurate
- Some tracks may fail if unavailable

---

## 📜 License

MIT
