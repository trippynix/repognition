import re
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_java(file_path):
    """Parse Java code into structured chunks:
    - Classes, interfaces, enums, methods, and annotations are captured fully.
    - Remaining code (imports, variables, loose statements) is chunked separately.
    """

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Regex for Java structures
    pattern = r"""(
        (?:@\w+(?:\([^)]*\))?)                                  # Annotations
        |(?:class\s+\w+(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w, ]+)?\s*{[\s\S]*?})  # Classes
        |(?:interface\s+\w+\s*{[\s\S]*?})                       # Interfaces
        |(?:enum\s+\w+\s*{[\s\S]*?})                            # Enums
        |(?:(?:public|private|protected)?\s*(?:static\s+)?      # Methods / Constructors
           (?:<.*?>\s*)?[\w\[\]<>]+\s+\w+\s*\([^)]*\)\s*{[\s\S]*?})
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
        if chunk_text.startswith("@"):
            chunk_type = "annotation"
        elif chunk_text.startswith("class"):
            chunk_type = "class"
        elif chunk_text.startswith("interface"):
            chunk_type = "interface"
        elif chunk_text.startswith("enum"):
            chunk_type = "enum"
        else:
            chunk_type = "function"  # catch-all for methods

        chunks.append(
            {
                "type": chunk_type,
                "content": chunk_text,
                "start_line": start_line,
                "end_line": end_line,
            }
        )

        used_lines.update(range(start_line, end_line + 1))

    # --- 2. Capture remaining lines (variables, imports, misc code) ---
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
