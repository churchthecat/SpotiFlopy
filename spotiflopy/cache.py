import os
import json
import hashlib

CACHE_FILE = os.path.expanduser("~/.spotiflopy_cache.json")


def _load():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def _save(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def _key(query):
    return hashlib.md5(query.encode()).hexdigest()


def get(query):
    cache = _load()
    return cache.get(_key(query))


def set(query, results):
    cache = _load()
    cache[_key(query)] = results
    _save(cache)
