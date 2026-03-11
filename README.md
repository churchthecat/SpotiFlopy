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
* Automatic YouTube downloads
* Artist / Album folder structure
* Embedded album artwork
* Proper ID3 tags
* Duplicate tracking
* Cron automation
* Linux server support
* Headless authentication
* CLI tool (`spotiflopy`)

---

# Demo

Example run:

```
$ spotiflopy

Syncing Spotify liked songs...

✔ Electro Spectre - The Bell
✔ VNV Nation - Nova
✔ Flogging Molly - What's Left of the Flag

Download complete.
```

Example folder structure:

```
Music/
 └── SpotiFlopy/
     ├── Artist/
     │   └── Album/
     │       ├── 01 - Track.mp3
     │       └── 02 - Track.mp3
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

After installation you can run SpotiFlopy via CLI.

Basic usage:

```
spotiflopy
```

Commands:

```
spotiflopy sync
spotiflopy login
spotiflopy doctor
```

| Command           | Description       |
| ----------------- | ----------------- |
| spotiflopy        | Sync liked songs  |
| spotiflopy sync   | Manual sync       |
| spotiflopy login  | Re-authenticate   |
| spotiflopy doctor | Check environment |

---

# Spotify Authentication

SpotiFlopy supports **two authentication methods**.

---

# Option A — Localhost Authentication (Recommended)

Use when running locally.

Create Spotify application:

https://developer.spotify.com/dashboard

Add redirect URI:

```
http://localhost:8888/callback
```

Create `.env`

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

Run:

```
spotiflopy
```

Browser will open for login.

Token stored locally:

```
.spotiflofy_token_cache
```

---

# Option B — Cloudflare Tunnel (Headless Servers)

Use when running on:

* VPS
* remote servers
* headless machines
* environments without browsers

Example proxy:

https://github.com/1111ij1/spotify-proxy

Example `.env`

```
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIPY_REDIRECT_URI=https://your-domain.com/callback
```

The proxy handles OAuth authentication.

---

# Automation (Cron)

Automatically sync your Spotify library.

```
crontab -e
```

Example:

```
0 2,14 * * * /home/user/SpotiFlopy/myenv/bin/spotiflopy >> /home/user/spotiflopy.log 2>&1
```

Runs twice daily.

---

# YouTube Cookies (Avoid Bot Detection)

YouTube may require browser cookies.

SpotiFlopy attempts to use cookies from:

* Chrome
* Chromium
* Brave
* Firefox

Install Chromium on servers:

```
sudo apt install chromium-browser
```
# YouTube Cookies (Optional)

If YouTube blocks downloads you can export cookies.

Install the "Get cookies.txt" browser extension.

Export cookies from YouTube and place the file in the project folder:

cookies.txt

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

### YouTube "Sign in to confirm you're not a bot"

Install a browser:

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
 ├── main.py
 ├── requirements.txt
 ├── setup.py
 ├── README.md
 ├── songs.csv
 ├── .env
 └── myenv/
```

---

# Credits

This project is based on the original **SpotiFlopy** by:

https://github.com/aneeb02/SpotiFlopy

The project has been extended with:

* CLI interface
* automation
* improved authentication
* headless support
* improved download handling

Huge thanks to the original author.

---

# Roadmap

Possible future improvements:

* Playlist syncing
* FLAC downloads
* MusicBrainz metadata matching
* Download progress bars
* Web UI

---

# Contributing

Pull requests are welcome.

If you find bugs or improvements, open an issue or submit a PR.

---

# License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies.
