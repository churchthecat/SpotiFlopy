# 🎧 SpotiFlopy

Spotify → local music sync tool.

Sync your Spotify liked songs and playlists into a clean, tagged, deduplicated local music library with smart matching, incremental sync, and upgrade support.

---

## ✨ Features

- Sync liked songs and playlists
- Parallel downloads + retry queue
- Incremental sync (no re-downloads)
- Smart matching (filename + audio fingerprint)
- Optional AcoustID matching
- MusicBrainz metadata + album art
- Playlist sync using symlinks (no duplicates)
- MP3 + FLAC support
- Smart upgrade system (MP3 → FLAC auto replace)
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
- Music folder
- Audio format (mp3 / flac / best)
- Optional AcoustID API key

---

## 🔑 Spotify App Setup (Local) Easy

Create an app:

https://developer.spotify.com/dashboard

Set redirect URI EXACTLY:

http://127.0.0.1:8888/callback

Then run:

spotiflopy sync

A browser will open for authentication.

---

## ☁️ Headless / Server Setup (Cloudflare Proxy) Recommended

For servers, VPS, or headless setups, you can use a public HTTPS callback via Cloudflare.

### 1. Create a public endpoint

Use Cloudflare Tunnel (or any reverse proxy) to expose your local callback:

Example:

https://your-domain.com/callback

### 2. Add it to Spotify

In your Spotify app dashboard, add:

https://your-domain.com/callback

### 3. Configure SpotiFlopy

During `spotiflopy init`, use:

Redirect URI:

https://your-domain.com/callback

Example project:

https://github.com/1111ij1/spotify-proxy

### 4. Run sync

spotiflopy sync

👉 Spotify will redirect to your public URL  
👉 Your proxy forwards it to your local app  

---

## ▶️ Usage

Sync liked songs:

spotiflopy sync

Sync playlists:

spotiflopy sync --playlists

Limit + workers:

spotiflopy sync --limit 10 --workers 4

Repair library:

spotiflopy repair

---

## 🧠 Matching System

1. Filename match (fast)
2. Audio fingerprint (Chromaprint / fpcalc)
3. AcoustID lookup (optional)

---

## 🔼 Smart Upgrade

If switching to FLAC:

- Existing MP3 detected
- FLAC downloaded
- MP3 replaced automatically
- No duplicates kept

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

sudo apt install ffmpeg chromium-browser

---

## ⚠️ Notes

- Spotify does NOT provide audio files
- Audio is sourced via yt-dlp
- FLAC may be re-encoded depending on source
- AcoustID improves matching accuracy but is optional

---

## 📜 License

MIT
	