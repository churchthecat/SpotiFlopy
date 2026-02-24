# SpotiFlopy 🎵

Automatically download all your Spotify Liked Songs as organized, high-quality MP3 files.

---

## ✨ Features

- Fetches all your Spotify Liked Songs using the Spotify API  
- Downloads audio from YouTube using `yt-dlp`  
- Converts to high-quality MP3 (192kbps)  
- Automatically embeds metadata and thumbnail  
- Organizes music by **Artist → Album → Track Number**  
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


The folder is reused automatically on future runs.

### Change Folder Later

```bash
python main.py --change-folder
⚙️ How It Works

Uses the Spotify API to fetch your Liked Songs

Checks if songs are already downloaded

Searches YouTube for the official audio

Downloads and converts to MP3 using yt-dlp

Saves songs in structured folders:

Artist/
 └── Album/
      └── 01 - Track Name.mp3

Tracks downloads in songs.csv

🔧 Installation
1️⃣ Clone the Repository
git clone https://github.com/yourusername/SpotiFlopy.git
cd SpotiFlopy
2️⃣ Create Virtual Environment (Recommended)

Install required system packages (Debian/Ubuntu):

sudo apt install python3-full python3-venv

Create and activate virtual environment:

python3 -m venv myenv
source myenv/bin/activate

Upgrade pip:

python -m pip install --upgrade pip

Install dependencies:

pip install -r requirements.txt
3️⃣ Set Up Spotify API Credentials

You need Spotify API credentials from:

👉 https://developer.spotify.com/dashboard

✅ Option A — Local Redirect (Standard Method)

Create a new app

Add this Redirect URI:

http://localhost:8888/callback/

Create a .env file in the project root:

SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback/

This runs a temporary local webserver for authentication.

🌍 Option B — Cloudflare Tunnel (Remote / Headless Systems)

If running on:

Remote server

VPS

Headless machine

Behind NAT

Or you want a public HTTPS redirect

Use:

👉 https://github.com/1111ij1/spotify-proxy

This allows:

Public HTTPS callback

No local browser requirement

Remote authentication

Your .env would look like:

SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=https://your-cloudflare-domain/callback/

Make sure the same HTTPS callback is added in the Spotify Developer Dashboard.

▶️ Run the Script
python main.py
First Run Will:

Open browser for Spotify authentication

Ask you to select a download folder (only once)

After That:

No prompts

Automatic syncing

Only new liked songs are downloaded

🔄 Change Download Folder Later
python main.py --change-folder
📦 Dependencies

spotipy

yt-dlp

python-dotenv