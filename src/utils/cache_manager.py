# src/utils/cache_manager.py
import os
import json
import hashlib


def get_cache_path(repo_name):
    """Generates the file path for the cache."""
    return f"data/{repo_name}_cache.json"


def load_cache(repo_name):
    """Loads the file hash cache from disk."""
    cache_path = get_cache_path(repo_name)
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}


def save_cache(repo_name, cache_data):
    """Saves the file hash cache to disk."""
    cache_path = get_cache_path(repo_name)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(cache_data, f, indent=2)


def calculate_file_hash(file_path):
    """Calculates the SHA256 hash of a file's content."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None
