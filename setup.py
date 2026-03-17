from setuptools import setup, find_packages

setup(
    name="spotiflopy",
    version="2.3.1",
    packages=find_packages(),
    install_requires=[
        "spotipy",
        "yt-dlp",
        "mutagen",
        "requests",
        "musicbrainzngs"
    ],
    entry_points={
        "console_scripts": [
            "spotiflopy=spotiflopy.main:main"
        ]
    },
)
