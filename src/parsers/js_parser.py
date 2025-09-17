import re
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_js(file_path):
    """Extract JS functions/classes using regex."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = r"(function\s+\w+\s*\([^)]*\)\s*{[^}]*}|class\s+\w+\s*{[^}]*})"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return splitter.split_text(content)

    return matches
