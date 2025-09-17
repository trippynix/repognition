import os


def chunk_with_metadata(file_path, chunks, all_current_chunks, lang=None):
    """Attach metadata to chunks."""
    data = []
    for i, chunk in enumerate(chunks):
        last_index = all_current_chunks[-1]["chunk_id"] if all_current_chunks else 0
        entry = {
            "repo": os.path.basename(os.path.dirname(file_path)),
            "file_path": file_path,
            "lang": lang,
            "chunk_id": last_index + i + 1,
            "content": chunk.strip(),
        }
        data.append(entry)
    return data
