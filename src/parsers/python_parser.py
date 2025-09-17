import ast
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_python_with_ast(file_path):
    """Parse Python code into function/class chunks using AST."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return splitter.split_text(content)

    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = getattr(node, "end_lineno", start_line + 1)
            lines = content.splitlines()[start_line:end_line]
            chunks.append("\n".join(lines))

    if not chunks:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(content)

    return chunks
