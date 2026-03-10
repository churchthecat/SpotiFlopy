# SpotiFlopy

Automatically mirror your Spotify liked songs locally.

SpotiFlopy syncs your Spotify library and downloads the audio from YouTube using **Spotipy** and **yt-dlp**.

Features

* Sync Spotify liked songs
* Automatic download from YouTube
* Artist / Album folder structure
* Embedded album artwork
* Proper ID3 tags
* Duplicate tracking
* Cron automation
* Works on Linux servers and desktops
* Supports headless environments

---

# Installation

Clone the repository

```
git clone https://github.com/churchthecat/SpotiFlopy.git
cd SpotiFlopy
```

Create a virtual environment

```
python3 -m venv myenv
source myenv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

Install ffmpeg (required for audio conversion)

```
sudo apt update
sudo apt install ffmpeg
```

---

# Spotify API Setup

Create a Spotify application:

https://developer.spotify.com/dashboard

Create a new app and copy the credentials.

Add the redirect URI:

```
http://localhost:8888/callback
```

---

# Environment Configuration

Create a `.env` file in the project root.

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

---

# Run SpotiFlopy

```
python main.py
```

On first run you will be asked for the download folder.

Example:

```
Download folder [/home/user/Music/SpotiFlopy]:
```

Press enter to accept the default.

---

# Example Download Structure

```
Music/
 └── SpotiFlopy/
     ├── Artist
     │   ├── Album
     │   │   ├── 01 - Track.mp3
     │   │   ├── 02 - Track.mp3
     │   │   └── 03 - Track.mp3
```

Each file includes:

* title
* artist
* album
* track number
* album artwork

---

# Automation (Cron)

You can automatically sync your Spotify library.

Edit your cron jobs

```
crontab -e
```

Run twice per day

```
0 2,14 * * * /home/user/SpotiFlopy/myenv/bin/python /home/user/SpotiFlopy/main.py >> /home/user/spotiflopy.log 2>&1
```

---

# Cookies for YouTube (Avoid Bot Detection)

YouTube may require browser cookies.

SpotiFlopy automatically tries to use cookies from:

* Chrome
* Chromium
* Brave
* Firefox

If none are found, install a browser or export cookies manually.

---

# 🌍 Option B — Cloudflare Tunnel (Headless / Remote Servers)

If you run SpotiFlopy on:

* a **remote server**
* a **VPS**
* a **headless machine**
* behind **strict NAT**
* or want a cleaner production-style OAuth redirect

you can use a **Cloudflare-based proxy** instead of localhost authentication.

Example proxy project:

https://github.com/1111ij1/spotify-proxy

This allows you to:

* Avoid localhost redirects
* Use a **public HTTPS callback**
* Authenticate remotely
* Run fully headless
* Use SpotiFlopy on servers without a browser

Example `.env` configuration:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=https://your-domain.com/callback
```

---

# Security Notes

The following files should **never be committed to GitHub**:

```
.env
.spotiflofy_token_cache
.spotiflofy_config.json
cookies.txt
```

These are already excluded in `.gitignore`.

---

# Updating

Pull latest updates

```
git pull origin main
```

Update dependencies

```
pip install -r requirements.txt
```


---

# Running as a Background Service (Recommended)

Instead of cron, you can run SpotiFlopy as a **systemd service**.
This is more reliable and easier to monitor.

Create a service file:

```id="svc1"
sudo nano /etc/systemd/system/spotiflopy.service
```

Paste:

```id="svc2"
[Unit]
Description=SpotiFlopy Spotify Sync
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/SpotiFlopy
ExecStart=/home/YOUR_USERNAME/SpotiFlopy/myenv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your Linux username.

Enable the service:

```id="svc3"
sudo systemctl daemon-reload
sudo systemctl enable spotiflopy
```

Start it:

```id="svc4"
sudo systemctl start spotiflopy
```

Check status:

```id="svc5"
systemctl status spotiflopy
```

---

# View Logs

View live logs

```id="log1"
journalctl -u spotiflopy -f
```

This shows downloads and errors in real time.

---

# Automatic Updates

You can automatically update the project from GitHub.

Pull latest changes:

```id="git1"
cd ~/SpotiFlopy
git pull origin main
pip install -r requirements.txt
```

---

# Updating Dependencies

Keep yt-dlp updated frequently because YouTube changes often.

```id="upd1"
pip install -U yt-dlp
```

---

# Troubleshooting

### YouTube "Sign in to confirm you're not a bot"

Make sure a browser is installed so cookies can be used.

Supported browsers:

* Chrome
* Chromium
* Brave
* Firefox

Install Chromium for servers:

```id="tr1"
sudo apt install chromium-browser
```

---

### Spotify authentication loop

Delete the token cache:

```id="tr2"
rm .spotiflopy_token_cache
```

Then run again.

---

# Roadmap

Possible future improvements:

* Playlist syncing
* Automatic metadata correction
* FLAC downloads
* MusicBrainz matching
* Download progress bars
* Web UI

---

# Contributing

Pull requests are welcome.

If you find bugs or have improvements, feel free to open an issue or submit a PR.

---

# Project Structure

```id="tree"
SpotiFlopy/
 ├── main.py
 ├── requirements.txt
 ├── README.md
 ├── .env
 ├── songs.csv
 └── myenv/
```

---

# Author

Created for personal Spotify library mirroring and automation.

---

# License

MIT License


---

# License

MIT License

---

# Disclaimer

SpotiFlopy downloads audio from YouTube for personal use.
Ensure you comply with local copyright laws and the terms of service of the platforms you use.
