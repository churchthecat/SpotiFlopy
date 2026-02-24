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

Default:

```
~/Desktop/Songs
```

On first run you can choose a custom folder.

Configuration is stored in:

```
~/.spotiflopy_config.json
```

The folder is reused automatically on future runs.

### Change Folder Later

```bash
python main.py --change-folder
```

---

## ⚙️ How It Works

- Uses Spotify API to fetch your liked songs  
- Checks if songs already exist locally  
- Searches YouTube for official audio  
- Downloads and converts to MP3 using `yt-dlp`  
- Saves songs in structured folders:

```
Artist/
 └── Album/
      └── 01 - Track Name.mp3
```

- Tracks downloads in `songs.csv`

---

## 🔧 Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/SpotiFlopy.git
cd SpotiFlopy
```

---

### Create Virtual Environment (Recommended)

Install system dependencies:

```bash
sudo apt install python3-full python3-venv
```

Create and activate environment:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Spotify API Setup

Create credentials at:

https://developer.spotify.com/dashboard

---

### Option A — Local Redirect (Standard)

1. Create a new app  
2. Add redirect URI:

```
http://localhost:8888/callback/
```

3. Create a `.env` file in the project root:

```
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback/
```

---

### Option B — Cloudflare / Remote Setup

For:

- Remote server  
- VPS  
- Headless machine  
- Public HTTPS callback  

Use:

https://github.com/1111ij1/spotify-proxy

Your `.env` would look like:

```
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=https://your-cloudflare-domain/callback/
```

Make sure the redirect URL matches what you set in the Spotify dashboard.

---

## ▶️ Run

```bash
python main.py
```

### First Run

- Opens browser for Spotify authentication  
- Asks for download folder (once)  

---

### After That

- No prompts  
- Automatic syncing  
- Only new liked songs are downloaded  

---

## 🔄 Change Folder Later

```bash
python main.py --change-folder
```

---

## 📦 Dependencies

- spotipy  
- yt-dlp  
- python-dotenv  

---

## 🚀 About

Automatically download your Spotify liked songs locally with automatic organization and metadata support.