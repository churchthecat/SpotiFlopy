# SpotiFlopy 🎵

Automatically download all your **Spotify Liked Songs** as organized, high-quality MP3 files.

SpotiFlopy connects to the Spotify API, retrieves your liked songs, finds the best matching audio on YouTube, and downloads them as tagged MP3 files organized by artist and album.

---

# ✨ Features

<<<<<<< HEAD
- Fetches all your Spotify Liked Songs using the Spotify API  
- Downloads audio from YouTube using `yt-dlp`  
- Converts to high-quality MP3 (192kbps)  
- Automatically embeds metadata and thumbnail  
- Organizes music by **Artist → Album → Track Number**  
- Remembers your selected download folder  
- Skips already downloaded tracks  
- Maintains a `songs.csv` tracker  
- Supports local or Cloudflare-based OAuth redirect  
=======
* Fetches all your **Spotify Liked Songs**
* Downloads audio using **yt-dlp**
* Converts to **192kbps MP3**
* Automatically embeds **metadata + thumbnail**
* Organizes files by **Artist → Album → Track Number**
* Remembers your chosen download folder
* **Skips already downloaded tracks**
* Maintains a **songs.csv tracker**
* Works locally or on **headless servers**
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

---

# 📁 Download Location

<<<<<<< HEAD
Default:
=======
By default, songs are saved to:
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

```
~/Desktop/Songs
```

<<<<<<< HEAD
On first run you can choose a custom folder.

Configuration is stored in:
=======
On first run you may choose a different location.

Your selection is saved in:
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

```
~/.spotiflopy_config.json
```

<<<<<<< HEAD
The folder is reused automatically on future runs.

### Change Folder Later
=======
To change the folder later:
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

```
python main.py --change-folder
```

---

<<<<<<< HEAD
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
=======
# ⚙️ How It Works

1. Uses the **Spotify API** to fetch your liked songs
2. Checks if tracks already exist locally
3. Searches YouTube for the **official audio**
4. Downloads the best audio stream
5. Converts to MP3 using **ffmpeg**
6. Embeds metadata and thumbnail
7. Tracks downloads in **songs.csv**

Music is saved like this:

```
Artist/
   Album/
      01 - Track Name.mp3
```

Example `songs.csv` entry:

```
Artist,Album,Track,Track Number
Rancid,...And Out Come The Wolves,Roots Radical,03
```

---

# 📂 Project Structure

```
SpotiFlopy/
│
├── main.py
├── requirements.txt
├── README.md
│
├── cookies.txt        (optional)
├── .env               (not committed)
│
└── songs.csv          (created automatically)
```

---

# 🔧 Installation

## 1️⃣ Clone the Repository

```
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)
git clone https://github.com/yourusername/SpotiFlopy.git
cd SpotiFlopy
```

---

<<<<<<< HEAD
### Create Virtual Environment (Recommended)

Install system dependencies:

```bash
sudo apt install python3-full python3-venv
```

Create and activate environment:

```bash
=======
## 2️⃣ Install System Dependencies

Ubuntu / Debian:

```
sudo apt install python3-full python3-venv ffmpeg
```

---

## 3️⃣ Create a Virtual Environment

```
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)
python3 -m venv myenv
source myenv/bin/activate
```

Upgrade pip:

<<<<<<< HEAD
```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
=======
```
python -m pip install --upgrade pip
```

Install Python dependencies:

```
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)
pip install -r requirements.txt
```

---

<<<<<<< HEAD
## 🔐 Spotify API Setup

Create credentials at:

https://developer.spotify.com/dashboard

---

### Option A — Local Redirect (Standard)

1. Create a new app  
2. Add redirect URI:
=======
# 📦 Dependencies

Python packages:

```
spotipy
yt-dlp
python-dotenv
secretstorage
```

System requirement:

```
ffmpeg
```

---

# 🔑 Spotify API Setup

Create API credentials from the Spotify Developer Dashboard:

https://developer.spotify.com/dashboard

Create a new app and add this redirect URI:
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

```
http://localhost:8888/callback/
```

<<<<<<< HEAD
3. Create a `.env` file in the project root:
=======
Create a `.env` file in the project root:
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

```
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback/
```

<<<<<<< HEAD
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
=======
⚠ **Never upload `.env` to GitHub**

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
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)

```
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
<<<<<<< HEAD
SPOTIPY_REDIRECT_URI=https://your-cloudflare-domain/callback/
```

Make sure the redirect URL matches what you set in the Spotify dashboard.

---

## ▶️ Run

```bash
=======
SPOTIPY_REDIRECT_URI=https://your-domain/callback/
```

Make sure the same callback URL is added in:

**Spotify Developer Dashboard → Redirect URIs**

---

# 🍪 YouTube Cookie Setup (Recommended)

YouTube sometimes blocks automated downloads.

Exporting cookies from your browser prevents most **bot detection issues**.

Run:

```
yt-dlp --cookies-from-browser chromium --cookies cookies.txt https://youtube.com
```

This creates:

```
cookies.txt
```

SpotiFlopy will automatically use it if present.

---

# ▶️ Running SpotiFlopy

Run the script:

```
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)
python main.py
```

### First Run

<<<<<<< HEAD
- Opens browser for Spotify authentication  
- Asks for download folder (once)  

---

### After That

- No prompts  
- Automatic syncing  
- Only new liked songs are downloaded  

---

## 📦 Dependencies

- spotipy  
- yt-dlp  
- python-dotenv  

---

## 🚀 About

Automatically download your Spotify liked songs locally with automatic organization and metadata support.
=======
* Open a browser for **Spotify authentication**
* Ask you to select a **download folder**
* Start syncing your liked songs

Future runs will:

* Skip existing tracks
* Only download **new liked songs**

---

# 🔄 Change Download Folder Later

```
python main.py --change-folder
```

---

# 🔒 Security Notes

The following files **must never be committed to GitHub**:

```
.env
cookies.txt
.spotiflopy_token_cache
.spotiflopy_config.json
```

Recommended `.gitignore`:

```
.env
cookies.txt
.spotiflopy_token_cache
.spotiflopy_config.json
__pycache__/
myenv/
songs/
```

---

# ⚠ Disclaimer

This project is intended for **personal use only**.

Respect the terms of service of Spotify and YouTube and comply with local copyright laws.

---

# 📜 License

MIT License
>>>>>>> 6aed943 (Improve README, add env example, update dependencies and cleanup)
