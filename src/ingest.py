import os
import json
from parsers.python_parser import parse_python_with_ast
from parsers.js_parser import parse_js
from parsers.java_parser import parse_java
from parsers.markdown_parser import markdown_split
from utils.github_cloner import clone_github_repo
from utils.gitignore_loader import load_gitignore
from utils.metadata import chunk_with_metadata


def get_chunks_from_repo(repo_path):
    all_chunks = []
    spec = load_gitignore(repo_path)
    # spec = None

    for root, dirs, files in os.walk(repo_path):
        rel_root = os.path.relpath(root, repo_path)
        dirs[:] = [
            d for d in dirs if not (spec and spec.match_file(os.path.join(rel_root, d)))
        ]

        for file in files:
            rel_file_path = os.path.join(rel_root, file)
            if spec and spec.match_file(rel_file_path):
                continue

            file_path = os.path.join(root, file)
            if file.endswith((".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".bin")):
                continue

            if file.endswith(".py"):
                chunks = parse_python_with_ast(file_path)
                all_chunks.extend(
                    chunk_with_metadata(file_path, chunks, all_chunks, "python")
                )

            elif file.endswith(".js"):
                chunks = parse_js(file_path)
                all_chunks.extend(
                    chunk_with_metadata(file_path, chunks, all_chunks, "javascript")
                )

            elif file.endswith(".java"):
                chunks = parse_java(file_path)
                all_chunks.extend(
                    chunk_with_metadata(file_path, chunks, all_chunks, "java")
                )

            elif file.endswith((".md", ".txt")):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                chunks = markdown_split(content)
                all_chunks.extend(
                    chunk_with_metadata(file_path, chunks, all_chunks, "markdown")
                )

    return all_chunks


if __name__ == "__main__":
    github_url = input("Enter the GitHub repo URL: ").strip()

    # 1️⃣ Clone dynamically
    repo_path = clone_github_repo(github_url, base_dir="repos")
    print("Cloned repo path:", repo_path)

    # 2️⃣ Parse repo and create chunks
    chunks = get_chunks_from_repo(repo_path)
    print(f"Total chunks created: {len(chunks)}")

    # 3️⃣ Save chunks to JSON
    os.makedirs("data", exist_ok=True)
    with open("data/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
