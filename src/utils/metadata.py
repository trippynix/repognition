from .summarizer import generate_summary, extract_keywords
import os


def chunk_with_metadata(
    file_path, chunks, all_current_chunks, lang=None, repo_name=None
):
    """Attach metadata (repo, file, language, line numbers, summary, keywords) to chunks."""

    if repo_name is None:
        repo_name = os.path.basename(os.path.dirname(file_path))

    if lang is None:
        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".md": "markdown",
        }
        lang = lang_map.get(ext, "unknown")

    last_index = all_current_chunks[-1]["chunk_id"] if all_current_chunks else 0
    data = []

    for i, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        summary = generate_summary(content)
        keywords = extract_keywords(content)

        entry = {
            "repo": repo_name,
            "file_path": file_path,
            "lang": lang,
            "chunk_id": last_index + i + 1,
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
            "content": content.rstrip(),
            "summary": summary,
            "keywords": keywords,
        }
        data.append(entry)

    return data
