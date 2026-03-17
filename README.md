cat <<'EOF' > README.md
# 🎧 SpotiFlopy

Spotify → local music sync tool.

Sync your Spotify liked songs and playlists into a clean, tagged, deduplicated local music library with smart matching, fingerprint verification, and ultra-fast pre-download scoring.

---

## ✨ Features

- Sync liked songs and playlists
- Smart YouTube matching (no wasted downloads)
- Audio fingerprint verification (Chromaprint)
- Local fingerprint cache (zero API calls after first match)
- Incremental sync (no re-downloads)
- Clean Spotify-based tagging (artist / album / track)
- Album artwork embedding
- Playlist sync using symlinks (no duplicates)
- MP3 + FLAC support
- Smart upgrade system (MP3 → FLAC auto replace)
- Clean folder structure

---

## 🚀 Install (Simple)

git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy
python3 -m venv myenv
source myenv/bin/activate
pip install -e .

---

## ⚙️ Setup (First Run)

Run:

spotiflopy init

You will be prompted for:

- Spotify Client ID
- Spotify Client Secret
- Redirect URI

Defaults:

http://127.0.0.1:8888/callback

---

## 🔑 Spotify App Setup (Local)

Create an app:

https://developer.spotify.com/dashboard

Add redirect URI EXACTLY:

http://127.0.0.1:8888/callback

Then run:

spotiflopy sync

A browser will open for authentication.

---

## ☁️ Headless / Server Setup (Cloudflare Proxy)

For servers / VPS / headless:

### 1. Create public callback

Use Cloudflare Tunnel (or similar):

https://your-domain.com/callback

### 2. Add to Spotify dashboard

https://your-domain.com/callback

### 3. During init use:

https://your-domain.com/callback

### 4. Run:

spotiflopy sync

👉 Spotify redirects to your domain  
👉 Proxy forwards to your app  

Example proxy project:

https://github.com/1111ij1/spotify-proxy

---

## ▶️ Usage

Sync liked songs:

spotiflopy sync

Sync playlists:

spotiflopy sync --playlists

Limit number of tracks:

spotiflopy sync --limit 10

---

## 🧠 Matching Pipeline

1. YouTube search (no download)
2. Score results (artist + title + duration)
3. Download best candidate
4. Audio fingerprint verification
5. Store fingerprint (local cache)
6. Apply Spotify metadata

Result:

✔ Fast  
✔ Accurate  
✔ No duplicate downloads  

---

## 🔼 Smart Upgrade (MP3 → FLAC)

- Detect existing MP3
- Download FLAC
- Replace automatically
- Keep library clean

---

## 📁 Structure

Music/
  Artist/
    Album/
      01 - Track.mp3

  Playlists/
    Playlist Name/
      Track -> symlink

---

## 🛠 Requirements

Python 3.10+  
ffmpeg  
yt-dlp  
fpcalc (Chromaprint)

Install (Debian/Ubuntu):

sudo apt install ffmpeg chromium-browser libchromaprint-tools

---

## ⚠️ Notes

- Spotify does NOT provide audio files
- Audio is sourced via YouTube (yt-dlp)
- Matching is best-effort but highly accurate
- FLAC may be re-encoded depending on source

---

## 📜 License

MIT
EOF