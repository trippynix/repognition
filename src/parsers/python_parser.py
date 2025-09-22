import ast
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_python_with_ast(file_path):
    """Parse Python into chunks (functions, classes, and other code)."""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    lines = content.splitlines()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return [
            {"type": "generic", "content": chunk, "start_line": None, "end_line": None}
            for chunk in splitter.split_text(content)
        ]

    chunks = []
    used_lines = set()

    # --- Capture functions/classes with exact line numbers ---
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno
            end_line = getattr(node, "end_lineno", None)

            if end_line is None:  # fallback for Python <3.8
                # crude fallback: scan forward until indentation drops or file ends
                end_line = start_line
                while end_line < len(lines) and lines[end_line].startswith((" ", "\t")):
                    end_line += 1

            node_code = "\n".join(lines[start_line - 1 : end_line])
            chunks.append(
                {
                    "type": (
                        "function" if isinstance(node, ast.FunctionDef) else "class"
                    ),
                    "content": node_code,
                    "start_line": start_line,
                    "end_line": end_line,
                }
            )
            used_lines.update(range(start_line, end_line + 1))

    # --- Capture remaining lines ---
    current_block = []
    block_start = None
    for i, line in enumerate(lines, start=1):
        if i not in used_lines:
            if block_start is None:
                block_start = i
            current_block.append(line)
        elif current_block:  # flush previous block
            non_func_code = "\n".join(current_block)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100
            )
            for chunk in splitter.split_text(non_func_code):
                chunks.append(
                    {
                        "type": "other",
                        "content": chunk,
                        "start_line": block_start,
                        "end_line": block_start + chunk.count("\n"),
                    }
                )
            current_block = []
            block_start = None

    # flush last block
    if current_block:
        non_func_code = "\n".join(current_block)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        for chunk in splitter.split_text(non_func_code):
            chunks.append(
                {
                    "type": "other",
                    "content": chunk,
                    "start_line": block_start,
                    "end_line": block_start + chunk.count("\n"),
                }
            )

    # --- Sort chunks in original file order ---
    chunks.sort(key=lambda c: c["start_line"] or 0)

    return chunks
