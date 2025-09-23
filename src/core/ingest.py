import os
import json
from parsers.python_parser import parse_python_with_ast
from parsers.js_parser import parse_js
from parsers.java_parser import parse_java
from parsers.markdown_parser import markdown_split
from utils.github_cloner import clone_github_repo
from utils.gitignore_loader import load_gitignore
from utils.metadata import chunk_with_metadata


class RepoIngestor:
    """Handles cloning a GitHub repo, parsing files, creating chunks, and saving them."""

    def __init__(self, github_url, base_dir="repos", save_path="data/chunks.json"):
        self.github_url = github_url
        self.base_dir = base_dir
        self.save_path = save_path
        self.repo_path = None
        self.chunks = []

    def clone_repo(self):
        """Clone the repo and set the local path."""
        self.repo_path = clone_github_repo(self.github_url, self.base_dir)
        print("Cloned repo path:", self.repo_path)
        return self.repo_path

    def parse_repo(self):
        """Parse the entire repo into chunks."""
        if not self.repo_path:
            raise ValueError("Repo not cloned yet. Call clone_repo() first.")

        all_chunks = []
        spec = load_gitignore(self.repo_path)

        for root, dirs, files in os.walk(self.repo_path):
            rel_root = os.path.relpath(root, self.repo_path)
            dirs[:] = [
                d
                for d in dirs
                if not (spec and spec.match_file(os.path.join(rel_root, d)))
            ]

            for file in files:
                rel_file_path = os.path.join(rel_root, file)
                if spec and spec.match_file(rel_file_path):
                    continue

                file_path = os.path.join(root, file)
                if file.endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".bin")
                ):
                    continue

                chunks = self._parse_file(file_path, all_chunks)
                all_chunks.extend(chunks)

        self.chunks = all_chunks
        print(f"Total chunks created: {len(self.chunks)}")
        return self.chunks

    def _parse_file(self, file_path, existing_chunks):
        """Dispatch parser based on file type and attach metadata."""
        file = os.path.basename(file_path)

        if file.endswith(".py"):
            chunks = parse_python_with_ast(file_path)
            lang = "python"
        elif file.endswith(".js"):
            chunks = parse_js(file_path)
            lang = "javascript"
        elif file.endswith(".java"):
            chunks = parse_java(file_path)
            lang = "java"
        elif file.endswith((".md", ".txt")):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            chunks = markdown_split(content)
            lang = "markdown"
        else:
            return []

        return chunk_with_metadata(file_path, chunks, existing_chunks, lang)

    def save_chunks(self):
        """Save all chunks to JSON."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        print(f"Chunks saved to {self.save_path}")
        return self.save_path

    def run(self):
        """Run the full ingestion pipeline: clone, parse, save."""
        self.clone_repo()
        self.parse_repo()
        self.save_chunks()
        return self.chunks


if __name__ == "__main__":
    github_url = input("Enter the GitHub repo URL: ").strip()
    ingestor = RepoIngestor(github_url)
    ingestor.clone_repo()
    ingestor.parse_repo()
    ingestor.save_chunks()
