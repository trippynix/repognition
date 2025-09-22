import re
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_js(file_path):
    """Parse JavaScript code into structured chunks:
    - Captures functions (regular, arrow, anonymous), classes, imports/exports, and variables.
    - Remaining code is split into 'other' chunks.
    """

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Regex for JS constructs
    pattern = r"""(
        (?:function\s+\w+\s*\([^)]*\)\s*{[\s\S]*?})              # Named functions
        |(?:\w+\s*=\s*function\s*\([^)]*\)\s*{[\s\S]*?})         # Function expressions
        |(?:\w+\s*=\s*\([^)]*\)\s*=>\s*{[\s\S]*?})               # Arrow functions
        |(?:class\s+\w+\s*{[\s\S]*?})                            # Classes
        |(?:export\s+(?:default\s+)?(?:function|class)\s+\w+[\s\S]*?{[\s\S]*?}) # Exports
        |(?:import\s+[^;]+;)                                     # Imports
        |(?:const\s+\w+\s*=\s*[^;]+;)                            # Const variables
        |(?:let\s+\w+\s*=\s*[^;]+;)                              # Let variables
        |(?:var\s+\w+\s*=\s*[^;]+;)                              # Var variables
    )"""

    matches = list(re.finditer(pattern, content, re.VERBOSE))

    chunks = []
    used_lines = set()

    # --- 1. Capture defined structures ---
    for match in matches:
        chunk_text = match.group(0).strip()
        start_line = content[: match.start()].count("\n") + 1
        end_line = content[: match.end()].count("\n") + 1

        # Determine type
        if chunk_text.startswith("class"):
            chunk_type = "class"
        elif chunk_text.startswith("function") or "=>" in chunk_text:
            chunk_type = "function"
        elif chunk_text.startswith("import"):
            chunk_type = "import"
        elif chunk_text.startswith("export"):
            chunk_type = "export"
        elif chunk_text.startswith(("const", "let", "var")):
            chunk_type = "variable"
        else:
            chunk_type = "other"

        chunks.append(
            {
                "type": chunk_type,
                "content": chunk_text,
                "start_line": start_line,
                "end_line": end_line,
            }
        )

        used_lines.update(range(start_line, end_line + 1))

    # --- 2. Capture remaining lines (loose statements, comments, misc code) ---
    remaining_lines = []
    for i, line in enumerate(content.splitlines(), start=1):
        if i not in used_lines:  # skip already captured lines
            remaining_lines.append(line)

    if remaining_lines:
        non_func_code = "\n".join(remaining_lines)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        for chunk in splitter.split_text(non_func_code):
            chunks.append(
                {
                    "type": "other",
                    "content": chunk,
                    "start_line": None,
                    "end_line": None,
                }
            )

    return chunks
