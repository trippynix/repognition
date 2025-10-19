# src/components/chunker.py
import os
from src.parsers.python_parser import parse_python_with_ast
from src.parsers.js_parser import parse_js
from src.parsers.java_parser import parse_java
from src.parsers.markdown_parser import markdown_split
from src.llm.ollama_client import enrich_chunk


def _parse_file(file_path):
    """Dispatcher to parse a file based on its extension."""
    if file_path.endswith(".py"):
        return parse_python_with_ast(file_path), "python"
    elif file_path.endswith(".js"):
        return parse_js(file_path), "javascript"
    elif file_path.endswith(".java"):
        return parse_java(file_path), "java"
    elif file_path.endswith((".md", ".txt")):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return markdown_split(content), "markdown"
    else:
        return [], "unknown"


def process_and_chunk_file(file_path, repo_name):
    """
    Parses a single file, adds metadata, and returns a list of chunks.
    (This is now a sequential operation for a single file).
    """
    raw_chunks, lang = _parse_file(file_path)
    if lang == "unknown":
        return []

    processed_chunks = []
    for i, chunk in enumerate(raw_chunks):
        content = chunk.get("content", "")

        # Enrich chunks one by one
        enriched_data = enrich_chunk(content)
        summary = enriched_data["summary"]
        keywords = enriched_data["keywords"]

        entry = {
            "repo": repo_name,
            "file_path": file_path,
            "lang": lang,
            "chunk_id": f"{os.path.basename(file_path)}-{i}",
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
            "content": content.rstrip(),
            "summary": summary,
            "keywords": keywords,
        }
        processed_chunks.append(entry)
    return processed_chunks
