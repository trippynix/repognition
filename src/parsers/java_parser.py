import re
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_java(file_path):
    """Extract Java methods/classes using regex."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = r"(class\s+\w+\s*{[^}]*}|(?:public|private|protected)?\s+\w+\s+\w+\s*\([^)]*\)\s*{[^}]*})"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return splitter.split_text(content)

    return matches
