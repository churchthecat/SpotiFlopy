# 🎧 SpotiFlopy

**Spotify → local, verified, high-quality music library sync tool.**

Sync your Spotify liked songs and playlists into a clean, tagged, deduplicated local music library with smart matching, verification, caching, and fast incremental sync.

---

## ✨ Features

* Sync liked songs and playlists
* Smart multi-stage YouTube matching (scoring + filtering)
* Pre-download scoring (avoid bad candidates early)
* Audio verification (duration + bitrate + sanity checks)
* Persistent caching (YouTube URLs + processed tracks)
* Incremental sync (skip existing files)
* Clean metadata tagging (ID3 + artwork embedding)
* Repair system (fix missing, broken, or incomplete tracks)
* SQLite-backed state tracking
* Modular architecture for easy extension

---

## 🚀 Install

```bash
git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy

python3 -m venv myenv
source myenv/bin/activate

pip install -e .
```

---

## ⚙️ Setup

Run:

```bash
spotiflopy init
```

You will be prompted for:

* Spotify Client ID
* Spotify Client Secret
* Redirect URI

Default:

```
http://127.0.0.1:8888/callback
```

---

## 🔑 Spotify App Setup (Local)

Create an app:

https://developer.spotify.com/dashboard

Add redirect URI EXACTLY:

```
http://127.0.0.1:8888/callback
```

Then run:

```bash
spotiflopy sync
```

---

## ☁️ Headless / Server Setup (Cloudflare Proxy)

### 1. Create public callback

```
https://your-domain.com/callback
```

### 2. Add to Spotify

```
https://your-domain.com/callback
```

### 3. Init

```bash
spotiflopy init
```

Use the same callback URL.

### 4. Run

```bash
spotiflopy sync
```

Flow:

```
Spotify → your domain → your local app
```

Example proxy:

https://github.com/1111ij1/spotify-proxy

---

## ▶️ Usage

Sync liked songs:

```bash
spotiflopy sync
```

Limit tracks:

```bash
spotiflopy sync --limit 10
```

Repair library:

```bash
spotiflopy repair
```

Full repair scan:

```bash
spotiflopy repair --full
```

---

## 🧠 Matching Pipeline

1. YouTube search
2. Pre-score (title + artist + duration)
3. Download best candidates only
4. Verify audio:

   * Duration match
   * Bitrate quality
   * File size sanity
5. Accept only high-score matches (≥ 0.8)
6. Cache YouTube URL
7. Apply metadata + cover

---

## ⚡ Performance

* Cached tracks skip search entirely
* Only top candidates are downloaded
* Verification prevents bad files early

---

## 📁 Output Structure

```
Music/
  Artist/
    Album/
      01 - Track.mp3
```

---

## 🧱 Project Structure

```
spotiflopy/
  cli.py            # CLI entrypoint
  download.py       # Sync + download logic
  spotify.py        # Spotify API integration
  youtube.py        # YouTube search (yt-dlp wrapper)
  verification.py   # Matching + validation
  matcher.py        # Candidate scoring
  tagger.py         # ID3 metadata tagging
  metadata.py       # Metadata helpers
  state.py / db.py  # Database + caching
  repair.py         # Repair logic
  playlist.py       # Playlist handling
  musicbrainz.py    # Metadata enrichment
  upgrade.py        # Migrations / upgrades

scripts/
  block_files.py    # Pre-commit safety checks
```

---

## 🛠 Requirements

* Python 3.10+
* ffmpeg
* yt-dlp

Install (Debian/Ubuntu):

```bash
sudo apt install ffmpeg yt-dlp
```

---

## 🔐 Configuration & Security

* Config is stored locally:

  ```
  ~/.spotiflopy_config.json
  ```
* Secrets are **never committed** to the repository
* Example config files contain placeholders only
* Runtime files (DB, cache, downloads, music) are ignored by git

If you accidentally commit secrets:

* Remove them immediately
* Rotate credentials (Spotify keys, etc.)

---
