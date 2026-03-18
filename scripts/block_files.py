import sys

BLOCKED_EXT = (
    ".db", ".db-shm", ".db-wal",
    ".mp3", ".webm", ".m4a"
)

BLOCKED_NAMES = (
    ".env",
    "cookies.txt",
    ".spotiflopy_config.json"
)

for file in sys.argv[1:]:
    if file.endswith(BLOCKED_EXT) or file in BLOCKED_NAMES or ".cache" in file:
        print(f"❌ BLOCKED: {file}")
        sys.exit(1)

sys.exit(0)
