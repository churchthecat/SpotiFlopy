# SpotiFlopy

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/github/license/churchthecat/SpotiFlopy)
![Repo Size](https://img.shields.io/github/repo-size/churchthecat/SpotiFlopy)

Automatically mirror your **Spotify liked songs locally**.

SpotiFlopy syncs your Spotify library and downloads audio from YouTube using **Spotipy** and **yt-dlp**.

---

# Features

- Sync Spotify liked songs
- Automatic YouTube downloads
- Artist / Album folder structure
- Embedded album artwork
- Duplicate tracking
- Cron automation
- Linux server support
- Headless authentication

---

# Quick Start

```
git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy

python3 -m venv myenv
source myenv/bin/activate

pip install -r requirements.txt

./spotiflopy sync
```

---

# Spotify Authentication

SpotiFlopy supports **two authentication methods**.

---

# Option A — Localhost Authentication

Use when running locally.

Add redirect URI in Spotify dashboard:

```
http://localhost:8888/callback
```

Create `.env`

```
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

Run:

```
./spotiflopy sync
```

Browser will open for login.

---

# Option B — Cloudflare Tunnel (Headless)

Use when running on:

- VPS
- remote servers
- headless machines

Example proxy:

https://github.com/1111ij1/spotify-proxy

Example `.env`

```
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI=https://your-domain.com/callback
```

---

# Automation (Cron)

Run twice daily.

```
crontab -e
```

Add:

```
0 2,14 * * * /home/user/SpotiFlopy/myenv/bin/python /home/user/SpotiFlopy/main.py >> /home/user/spotiflopy.log 2>&1
```

---

# YouTube Cookies

YouTube may require cookies.

SpotiFlopy automatically attempts to use cookies from:

- Chrome
- Chromium
- Brave
- Firefox

Install Chromium if needed:

```
sudo apt install chromium-browser
```

---

# Security

Never commit:

```
.env
.spotiflopy_token_cache
.spotiflopy_config.json
cookies.txt
```

---

# Updating

```
git pull
pip install -r requirements.txt
```

---

# License

MIT