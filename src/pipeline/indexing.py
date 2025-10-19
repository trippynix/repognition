# src/pipeline/indexing.py
import os
import json
from multiprocessing import Pool, cpu_count
from functools import partial
from src.components.git_cloner import clone_github_repo
from src.components.chunker import process_and_chunk_file
from src.components.vectorstore import VectorstoreManager
from src.utils.gitignore_loader import load_gitignore
from src.utils.cache_manager import load_cache, save_cache, calculate_file_hash
from config.settings import REPOS_DIR, CHUNKS_PATH, DATA_DIR


def process_file_wrapper(file_path, repo_name):
    """
    Wrapper to call process_and_chunk_file that always returns a tuple.
    """
    print(f"📄 Processing file: {file_path}")
    chunks = process_and_chunk_file(file_path, repo_name)
    return file_path, chunks


class IndexingPipeline:
    def __init__(self, github_url):
        self.github_url = github_url
        self.repo_name = github_url.split("/")[-1]
        self.vectorstore_manager = VectorstoreManager()
        self.repo_chunks_path = os.path.join(DATA_DIR, f"{self.repo_name}_chunks.json")

    def run(self):
        repo_path = clone_github_repo(self.github_url, REPOS_DIR)

        # 1. Load existing data and cache
        vectorstore = self.vectorstore_manager.load(self.repo_name)
        old_cache = load_cache(self.repo_name)
        all_chunks = []
        if os.path.exists(self.repo_chunks_path):
            with open(self.repo_chunks_path, "r", encoding="utf-8") as f:
                all_chunks = json.load(f)

        # 2. Identify file changes
        files_to_process = []
        new_cache = {}
        current_files = set()
        spec = load_gitignore(repo_path)

        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            rel_root = os.path.relpath(root, repo_path)
            if rel_root == ".":
                rel_root = ""

            if spec:
                # Filter directories in-place to prevent os.walk from traversing them
                dirs[:] = [
                    d for d in dirs if not spec.match_file(os.path.join(rel_root, d))
                ]
                # Filter files
                files = [
                    f for f in files if not spec.match_file(os.path.join(rel_root, f))
                ]

            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".bin")
                ):
                    continue

                current_files.add(file_path)
                file_hash = calculate_file_hash(file_path)
                new_cache[file_path] = file_hash

                if old_cache.get(file_path) != file_hash:
                    files_to_process.append(file_path)

        deleted_files = set(old_cache.keys()) - current_files

        if not files_to_process and not deleted_files:
            print("✨ No changes detected. Index is up to date!")
            return vectorstore

        # 3. Process only the changed files in parallel
        newly_processed_chunks = {}
        if files_to_process:
            print(f"Found {len(files_to_process)} new or modified files to process.")
            process_func = partial(process_file_wrapper, repo_name=self.repo_name)
            with Pool(processes=cpu_count()) as pool:
                results = pool.map(process_func, files_to_process)

            for file_path, chunks in results:
                newly_processed_chunks[file_path] = chunks

        # 4. Update the master chunk list
        # Remove chunks from deleted and modified files
        chunk_ids_to_remove = []
        files_to_update = set(newly_processed_chunks.keys()) | deleted_files

        remaining_chunks = []
        for chunk in all_chunks:
            if chunk["file_path"] in files_to_update:
                chunk_ids_to_remove.append(chunk["chunk_id"])
            else:
                remaining_chunks.append(chunk)

        # Add the newly processed chunks
        for file_path, chunks in newly_processed_chunks.items():
            remaining_chunks.extend(chunks)
        all_chunks = remaining_chunks

        # 5. Update vector store and save everything
        if not all_chunks:
            print("No chunks remaining or created. Exiting.")
            return None

        if vectorstore and chunk_ids_to_remove:
            vectorstore.delete(chunk_ids_to_remove)

        if newly_processed_chunks:
            # We need to format the new chunks for the vectorstore
            new_docs_for_vs = []
            for chunks in newly_processed_chunks.values():
                new_docs_for_vs.extend(chunks)

            if vectorstore:
                vectorstore = self.vectorstore_manager.add_documents(
                    vectorstore, new_docs_for_vs
                )
            else:
                # If no vectorstore exists, create a new one from all chunks
                print("Creating new FAISS vectorstore...")
                vectorstore = self.vectorstore_manager.create_vectorstore(all_chunks)

        self.vectorstore_manager.save(vectorstore, self.repo_name)
        save_cache(self.repo_name, new_cache)
        with open(self.repo_chunks_path, "w") as f:
            json.dump(all_chunks, f, indent=2)

        return vectorstore
