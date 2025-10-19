# src/pipeline/indexing.py
import os
import json
import time
import hashlib
from multiprocessing import Pool, cpu_count
from functools import partial
from src.components.git_cloner import clone_github_repo
from src.components.chunker import process_and_chunk_file
from src.components.vectorstore import VectorstoreManager
from src.utils.gitignore_loader import load_gitignore
from src.utils.cache_manager import load_cache, save_cache, calculate_file_hash
from config.settings import REPOS_DIR, DATA_DIR


def generate_directory_tree(repo_path):
    """Generates a string representation of the directory tree, respecting .gitignore."""
    tree_lines = []
    for root, dirs, files in os.walk(repo_path):
        # Exclude the .git directory
        if ".git" in dirs:
            dirs.remove(".git")

        rel_root = os.path.relpath(root, repo_path)
        if rel_root == ".":
            rel_root = ""

        level = rel_root.count(os.sep) if rel_root else 0
        indent = " " * 4 * level
        tree_lines.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = " " * 4 * (level + 1)
        for f in sorted(files):
            tree_lines.append(f"{sub_indent}{f}")
    return "\n".join(tree_lines)


def process_file_wrapper(file_path, repo_name):
    """Wrapper for multiprocessing to process a single file."""
    chunks = process_and_chunk_file(file_path, repo_name)
    return file_path, chunks


class IndexingPipeline:
    def __init__(self, github_url):
        self.github_url = github_url
        self.repo_name = github_url.split("/")[-1]
        self.vectorstore_manager = VectorstoreManager()
        self.repo_chunks_path = os.path.join(DATA_DIR, f"{self.repo_name}_chunks.json")

    def run(self, progress_callback=None):
        repo_path = clone_github_repo(self.github_url, REPOS_DIR)

        # 1. Load existing data
        vectorstore = self.vectorstore_manager.load(self.repo_name)
        old_cache = load_cache(self.repo_name)
        all_chunks = []
        if os.path.exists(self.repo_chunks_path):
            with open(self.repo_chunks_path, "r", encoding="utf-8") as f:
                all_chunks = json.load(f)

        # 2. Identify file and structure changes
        files_to_process = []
        new_cache = {}
        current_files = set()
        spec = load_gitignore(repo_path)

        # Tree structure capture
        directory_tree = generate_directory_tree(repo_path)
        tree_hash = hashlib.sha256(directory_tree.encode("utf-8")).hexdigest()
        tree_changed = old_cache.get("repository_structure.txt") != tree_hash
        new_cache["repository_structure.txt"] = tree_hash

        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            rel_root = os.path.relpath(root, repo_path)
            if rel_root == ".":
                rel_root = ""

            if spec:
                dirs[:] = [
                    d for d in dirs if not spec.match_file(os.path.join(rel_root, d))
                ]
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

        deleted_files = (
            set(old_cache.keys()) - current_files - {"repository_structure.txt"}
        )

        if not files_to_process and not deleted_files and not tree_changed:
            print("✨ No changes detected. Index is up to date!")
            if progress_callback:
                progress_callback(1, 1)
            return

        # 3. Process changed files in parallel
        newly_processed_chunks = {}
        if files_to_process:
            print(f"Found {len(files_to_process)} new or modified files to process.")
            process_func = partial(process_file_wrapper, repo_name=self.repo_name)

            with Pool(processes=cpu_count()) as pool:
                results_iterator = pool.imap_unordered(process_func, files_to_process)

                total_files = len(files_to_process)
                for i, (file_path, chunks) in enumerate(results_iterator):
                    newly_processed_chunks[file_path] = chunks
                    if progress_callback:
                        progress_callback(i + 1, total_files)

        # 4. Update the master chunk list
        files_to_update = set(newly_processed_chunks.keys()) | deleted_files
        if tree_changed:
            files_to_update.add("repository_structure.txt")

        chunk_ids_to_remove = []
        remaining_chunks = []
        for chunk in all_chunks:
            if chunk["file_path"] in files_to_update:
                chunk_ids_to_remove.append(chunk["chunk_id"])
            else:
                remaining_chunks.append(chunk)

        # Updating tree structure if it has changed
        if tree_changed:
            print("🌳 Directory structure has changed. Updating index.")
            tree_chunk = {
                "repo": self.repo_name,
                "file_path": "repository_structure.txt",
                "lang": "text",
                "chunk_id": "repository_structure-0",
                "start_line": None,
                "end_line": None,
                "content": directory_tree,
                "summary": "This document provides a tree-like representation of the repository's folder and file structure.",
                "keywords": "folder structure, directory tree, file layout, project architecture",
            }
            # Append the new tree chunk to remaining_chunks and newly_processed_chunks
            remaining_chunks.append(tree_chunk)
            if "repository_structure.txt" in newly_processed_chunks:
                newly_processed_chunks["repository_structure.txt"].append(tree_chunk)
            else:
                newly_processed_chunks["repository_structure.txt"] = [tree_chunk]

        # The loop below was causing duplication, this is a cleaner way
        temp_processed_chunks = []
        for chunks in newly_processed_chunks.values():
            temp_processed_chunks.extend(chunks)

        all_chunks = remaining_chunks + temp_processed_chunks

        # 5. Save everything
        if not all_chunks:
            print("No chunks remaining or created. Exiting.")
            return

        if vectorstore and chunk_ids_to_remove:
            existing_ids = set(vectorstore.index_to_docstore_id.values())
            # Ensure the list of IDs to delete is unique to prevent KeyErrors
            unique_ids_to_remove = set(chunk_ids_to_remove)
            valid_ids_to_delete = [
                id_ for id_ in unique_ids_to_remove if id_ in existing_ids
            ]
            if valid_ids_to_delete:
                vectorstore.delete(valid_ids_to_delete)

        # Collect all new chunks (from files and the tree) to be added to the vector store
        final_new_chunks = [
            chunk for chunks in newly_processed_chunks.values() for chunk in chunks
        ]

        if final_new_chunks:
            if vectorstore:
                vectorstore = self.vectorstore_manager.add_documents(
                    vectorstore, final_new_chunks
                )
            else:
                print("Creating new FAISS vectorstore...")
                vectorstore = self.vectorstore_manager.create_vectorstore(all_chunks)

        self.vectorstore_manager.save(vectorstore, self.repo_name)
        save_cache(self.repo_name, new_cache)
        with open(self.repo_chunks_path, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2)
