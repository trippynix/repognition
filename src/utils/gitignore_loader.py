from pathlib import Path
import pathspec


def load_gitignore(repo_path):
    gitignore_file = Path(repo_path) / ".gitignore"
    if gitignore_file.exists():
        with open(gitignore_file, "r", encoding="utf-8") as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        return spec
    return None
