# SpotiFlopy

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/github/license/churchthecat/SpotiFlopy)
![Repo Size](https://img.shields.io/github/repo-size/churchthecat/SpotiFlopy)
![Last Commit](https://img.shields.io/github/last-commit/churchthecat/SpotiFlopy)

Automatically mirror your **Spotify liked songs locally**.

SpotiFlopy syncs your Spotify library and downloads audio from YouTube using **Spotipy** and **yt-dlp**.

---

⭐ If you find this project useful, consider **starring the repository**.

---

# Features

* Sync Spotify liked songs
* Download Spotify playlists
* Automatic YouTube downloads
* Artist folder organization
* Embedded album artwork
* Proper ID3 tags
* Duplicate detection
* CLI tool (`spotiflopy`)
* Optional daemon auto-sync
* Cron automation
* Linux server support
* Headless authentication support
* Automatic browser cookie detection

---

# Demo

Example run:

```
$ spotiflopy sync

Syncing Spotify liked songs...

✔ Electro Spectre - The Bell
✔ VNV Nation - Nova
✔ Flogging Molly - What's Left of the Flag

Download complete.
```

Example folder structure:

```
Music/
 ├── VNV Nation/
 │   ├── Beloved.mp3
 │   └── Nova (Shine a Light on Me).mp3
 │
 ├── Electro Spectre/
 │   └── The Bell.mp3
```

---

# Quick Start

Install and run in under a minute.

```
git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy

python3 -m venv myenv
source myenv/bin/activate

pip install -r requirements.txt
pip install -e .

spotiflopy
```

First run will ask for your **music download folder**.

---

# Installation

Clone the repository:

```
git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy
```

Create virtual environment:

```
python3 -m venv myenv
source myenv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Install CLI command:

```
pip install -e .
```

Run:

```
spotiflopy
```

---

# CLI Usage

Basic usage:

```
spotiflopy
```

Commands:

```
spotiflopy sync
spotiflopy playlist PLAYLIST_URL
spotiflopy daemon
spotiflopy daemon 6
spotiflopy setdir
```

| Command                   | Description               |
| ------------------------- | ------------------------- |
| `spotiflopy`              | Sync liked songs          |
| `spotiflopy sync`         | Manual sync               |
| `spotiflopy playlist URL` | Download a playlist       |
| `spotiflopy daemon`       | Auto-sync every 12 hours  |
| `spotiflopy daemon 6`     | Auto-sync every 6 hours   |
| `spotiflopy setdir`       | Change download directory |

---

# Spotify Authentication

Create a Spotify application:

https://developer.spotify.com/dashboard

Add redirect URI:

```
http://localhost:8888/callback
```

Create `.env` file:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

Run:

```
spotiflopy
```

A browser window will open for authentication.

Token is stored locally:

```
.spotiflofy_token_cache
```

---

# Headless / Server Authentication

For headless systems (servers, VPS, containers), you can use an OAuth proxy.

Example project:

https://github.com/1111ij1/spotify-proxy

Example `.env`:

```
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI=https://your-domain.com/callback
```

The proxy handles the Spotify login flow.

---

# Automation (Cron)

Automatically sync your Spotify library.

Edit crontab:

```
crontab -e
```

Example:

```
0 2,14 * * * /home/user/SpotiFlopy/myenv/bin/spotiflopy >> /home/user/spotiflopy.log 2>&1
```

Runs twice daily.

---

# YouTube Cookies

YouTube may occasionally block downloads.

SpotiFlopy automatically attempts to extract cookies from installed browsers:

* Chrome
* Chromium
* Brave
* Firefox

If a browser is installed and logged into YouTube, downloads usually work automatically.

Example install for servers that works best with yt-dl:

```
sudo apt install chromium-browser
```

---

# Optional: Manual Cookies

If YouTube still blocks downloads, export cookies manually.

Install the browser extension:

```
Get cookies.txt
```

Export cookies from YouTube and place the file in the project folder:

```
cookies.txt
```

SpotiFlopy will automatically use it.

---

# Updating

Pull latest updates:

```
git pull
```

Update dependencies:

```
pip install -r requirements.txt
```

Update yt-dlp:

```
pip install -U yt-dlp
```

---

# Security Notes

Never commit these files:

```
.env
.spotiflofy_token_cache
.spotiflofy_config.json
cookies.txt
songs.csv
```

These are excluded in `.gitignore`.

---

# Troubleshooting

### YouTube: "Sign in to confirm you're not a bot"

Install Chromium:

```
sudo apt install chromium-browser
```

---

### Spotify login loop

Delete token cache:

```
rm .spotiflofy_token_cache
```

Run again.

---

# Project Structure

```
SpotiFlopy/
 ├── spotiflopy/
 │   ├── __init__.py
 │   └── main.py
 │
 ├── requirements.txt
 ├── pyproject.toml
 ├── setup.py
 ├── install.sh
 ├── README.md
 └── .env
```

---

# Credits

This project is based on the original **SpotiFlopy** by:

https://github.com/aneeb02/SpotiFlopy


Huge thanks to the original author.

---

# Roadmap

Possible future improvements:

* FLAC downloads
* MusicBrainz metadata matching
* Download progress bars
* Playlist auto-sync
* Web interface

---

# Contributing

Pull requests are welcome.

If you find bugs or improvements, open an issue or submit a PR.

---

# License

MIT License
