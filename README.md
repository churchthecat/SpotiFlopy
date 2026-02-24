# SpotiFlopy 🎵

Automatically download all your Spotify Liked Songs as organized, high-quality MP3 files.

---

## ✨ Features

- Fetches all your Spotify Liked Songs using the Spotify API
- Downloads audio from YouTube using `yt-dlp`
- Converts to high-quality MP3 (192kbps)
- Automatically embeds metadata and thumbnail
- Organizes music by Artist → Album → Track Number
- Remembers your selected download folder
- Skips already downloaded tracks
- Maintains a `songs.csv` tracker
- Supports local or Cloudflare-based OAuth redirect

---

## 📁 Download Location

By default, songs are saved to:


~/Desktop/Songs


On first run, you may choose a custom folder.

SpotiFlopy stores your selection in:


~/.spotiflopy_config.json


The folder will be reused automatically on future runs.

To change the folder later:

```bash
python main.py --change-folder
⚙️ How It Works

Uses the Spotify API to fetch your Liked Songs

Checks if songs are already downloaded

Searches YouTube for the official audio

Downloads and converts to MP3 using yt-dlp

Saves songs in structured folders:

Artist/
   Album/
      01 - Track Name.mp3

Tracks downloads in songs.csv

🔧 Installation
1️⃣ Clone the Repository
git clone https://github.com/yourusername/SpotiFlopy.git
cd SpotiFlopy
2️⃣ Create Virtual Environment (Recommended)

On Debian/Ubuntu systems:

sudo apt install python3-full python3-venv

Create and activate venv:

python3 -m venv myenv
source myenv/bin/activate

Upgrade pip:

python -m pip install --upgrade pip

Install dependencies:

pip install -r requirements.txt
3️⃣ Set Up Spotify API Credentials

You need Spotify API credentials from the Spotify Developer Dashboard.

✅ Option A — Local Redirect (Standard Method)

Go to: https://developer.spotify.com/dashboard

Create a new app

Add this Redirect URI:

http://localhost:8888/callback/

Create a .env file in the project root:

SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback/

This method runs a temporary local webserver during authentication.

🌍 Option B — Cloudflare Tunnel (Recommended for Remote / Headless Systems)

If you're running this on:

A remote server

A VPS

A headless machine

Behind strict NAT

Or want a cleaner production-style redirect

You can use a Cloudflare-based proxy:

https://github.com/1111ij1/spotify-proxy

This allows you to:

Avoid localhost redirects

Use a public HTTPS callback

Authenticate remotely

Run fully headless

In this case, your .env should look like:

SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=https://your-cloudflare-domain/callback/

Make sure the same HTTPS callback URL is added inside your Spotify Developer Dashboard.

▶️ Run the Script
python main.py

First run will:

Open a browser for Spotify authentication

Ask you to select a download folder (only once)

After that:

No prompts

Automatic syncing

Only new liked songs are downloaded

🔄 Change Download Folder Later
python main.py --change-folder
📦 Dependencies

spotipy

yt-dlp

python-dotenv
