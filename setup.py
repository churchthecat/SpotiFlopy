from setuptools import setup, find_packages

setup(
    name="spotiflopy",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "spotipy",
        "yt-dlp"
    ],
    entry_points={
        "console_scripts": [
            "spotiflopy=spotiflopy.main:main"
        ]
    }
)