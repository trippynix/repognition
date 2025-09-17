import os
from git import Repo
from urllib.parse import urlparse


def clone_github_repo(github_url, base_dir="repos"):
    """
    Clones a GitHub repository dynamically.

    Returns the local path of the cloned repo.
    """
    os.makedirs(base_dir, exist_ok=True)

    # Extract repo name from URL
    path_parts = urlparse(github_url).path.strip("/").split("/")
    repo_name = path_parts[-1].replace(".git", "")

    local_path = os.path.join(base_dir, repo_name)

    if os.path.exists(local_path):
        print(f"Repo already exists locally at {local_path}, pulling latest changes...")
        repo = Repo(local_path)
        repo.remotes.origin.pull()
    else:
        print(f"Cloning {github_url} into {local_path}...")
        Repo.clone_from(github_url, local_path)

    return local_path
