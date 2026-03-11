from setuptools import setup

setup(
    name="spotiflopy",
    version="0.1",
    description="Mirror Spotify liked songs locally",
    author="churchthecat",
    py_modules=["main"],
    install_requires=[
        "spotipy",
        "yt-dlp",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "spotiflopy=main:main"
        ]
    },
)