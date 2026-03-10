# SpotiFlopy 🎵

Automatically download your **Spotify Liked Songs** as organized MP3 files.

SpotiFlopy syncs your liked songs, finds the best match on YouTube, downloads the audio, and organizes everything into a clean music library.

---

# Features

• Sync Spotify liked songs
• Download audio using yt-dlp
• Convert to MP3 (192kbps)
• Embed metadata and thumbnails
• Organize files by Artist → Album → Track
• Skip already downloaded songs
• Maintain songs.csv tracker
• Parallel downloads for faster syncing
• Optional YouTube cookie support
• Works on desktops and servers

---

# Folder Structure

Example output:

Artist/
Album/
01 - Track Name.mp3

Tracker file:

songs.csv

Example:

Artist,Album,Track,Track Number
Rancid,...And Out Come The Wolves,Roots Radical,03

---

# Installation

Clone the repo:

git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy

Install system packages:

sudo apt install python3-full python3-venv ffmpeg

Create environment:

python3 -m venv myenv
source myenv/bin/activate

Install dependencies:

pip install -r requirements.txt

---

# Spotify API Setup

Create an app:

https://developer.spotify.com/dashboard

---

# Option A — Local Authentication

Redirect URI:

http://localhost:8888/callback/

Create `.env`:

SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback/

---

# Option B — Cloudflare Tunnel (Headless / Remote Servers)

If running SpotiFlopy on:

• VPS
• headless server
• remote machine
• strict NAT network

You can use a **Cloudflare proxy**.

Example project:

https://github.com/1111ij1/spotify-proxy

This provides:

• public HTTPS callback
• headless authentication
• remote login support

Example `.env`:

SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=https://your-domain.com/callback

---

# YouTube Cookie Setup

Optional but recommended.

Export cookies:

yt-dlp --cookies-from-browser chromium --cookies cookies.txt https://youtube.com

---

# Run the Script

python main.py

First run will authenticate Spotify and begin syncing.

Future runs download **only new songs**.

---

# Automation

Example cron job (twice per day):

0 2,14 * * * /home/user/SpotiFlopy/myenv/bin/python /home/user/SpotiFlopy/main.py >> /home/user/spotiflopy.log 2>&1

---

# Security Notes

Never commit:

.env
cookies.txt
.spotiflopy_token_cache
.spotiflopy_config.json
Songs/
myenv/

---

# License

MIT
