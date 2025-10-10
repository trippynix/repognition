# src/pipeline/indexing.py
import os
import json
from src.components.git_cloner import clone_github_repo
from src.components.chunker import process_and_chunk_file
from src.components.vectorstore import VectorstoreManager
from src.utils.gitignore_loader import load_gitignore
from config.settings import REPOS_DIR, CHUNKS_PATH


class IndexingPipeline:
    def __init__(self, github_url):
        self.github_url = github_url
        self.repo_name = github_url.split("/")[-1]
        self.vectorstore_manager = VectorstoreManager()

    def run(self):
        """Runs the full indexing pipeline: clone, chunk, and vectorize."""
        vectorstore = self.vectorstore_manager.load(self.repo_name)
        if vectorstore:
            print(
                f"Vectorstore for '{self.repo_name}' already exists. Skipping indexing."
            )
            return vectorstore

        repo_path = clone_github_repo(self.github_url, REPOS_DIR)

        all_chunks = []
        spec = load_gitignore(repo_path)
        for root, dirs, files in os.walk(repo_path):
            rel_root = os.path.relpath(root, repo_path)
            if rel_root == ".":
                rel_root = ""

            dirs[:] = [
                d
                for d in dirs
                if not (spec and spec.match_file(os.path.join(rel_root, d)))
            ]

            for file in files:
                rel_file_path = os.path.join(rel_root, file)
                if spec and spec.match_file(rel_file_path):
                    continue

                # --- ADD THIS LINE FOR VISIBILITY ---
                print(f"📄 Processing file: {rel_file_path}")
                # ------------------------------------

                file_path = os.path.join(root, file)
                if file.endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".bin")
                ):
                    continue

                chunks = process_and_chunk_file(file_path, self.repo_name)
                all_chunks.extend(chunks)

        if not all_chunks:
            print("No chunks were created. Exiting.")
            return None

        os.makedirs(os.path.dirname(CHUNKS_PATH), exist_ok=True)
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2)

        print("Creating new FAISS vectorstore...")
        vectorstore = self.vectorstore_manager.create_vectorstore(all_chunks)
        self.vectorstore_manager.save(vectorstore, self.repo_name)

        print("Indexing pipeline completed successfully!")
        return vectorstore
