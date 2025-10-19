# src/components/git_cloner.py
import os
from urllib.parse import urlparse

# Import git.Repo lazily to avoid import-time dependency on GitPython during tests.
try:
    from git import Repo
except Exception:  # pragma: no cover - fallback used only in test environments without GitPython
    Repo = None


def clone_github_repo(github_url, base_dir="repos"):
    """
    Clones a GitHub repository dynamically.
    Returns the local path of the cloned repo.
    """
    os.makedirs(base_dir, exist_ok=True)
    path_parts = urlparse(github_url).path.strip("/").split("/")
    repo_name = path_parts[-1].replace(".git", "")
    local_path = os.path.join(base_dir, repo_name)

    if os.path.exists(local_path):
        print(f"Repo already exists at {local_path}, pulling latest changes...")
        if Repo is None:
            # In environments without GitPython (like some test runs), we can't actually pull.
            # Raise a clear error so tests that expect a Repo instance can mock it.
            raise RuntimeError("GitPython not installed; cannot open existing repo at " + local_path)
        repo = Repo(local_path)
        repo.remotes.origin.pull()
    else:
        print(f"Cloning {github_url} into {local_path}...")
        if Repo is None:
            raise RuntimeError("GitPython not installed; cannot clone " + github_url)
        Repo.clone_from(github_url, local_path)

    return local_path
