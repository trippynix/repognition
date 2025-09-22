import re


def extract_identifiers(content, lang):
    """Extracts function/class names and variables depending on language."""
    identifiers = set()

    if lang == "python":
        identifiers.update(re.findall(r"def\s+(\w+)", content))
        identifiers.update(re.findall(r"class\s+(\w+)", content))

    elif lang in ["javascript", "typescript"]:
        identifiers.update(re.findall(r"function\s+(\w+)", content))
        identifiers.update(re.findall(r"class\s+(\w+)", content))
        identifiers.update(re.findall(r"const\s+(\w+)", content))
        identifiers.update(re.findall(r"let\s+(\w+)", content))
        identifiers.update(re.findall(r"var\s+(\w+)", content))

    elif lang == "java":
        identifiers.update(re.findall(r"class\s+(\w+)", content))
        identifiers.update(re.findall(r"interface\s+(\w+)", content))
        identifiers.update(re.findall(r"enum\s+(\w+)", content))
        identifiers.update(
            re.findall(r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(", content)
        )

    elif lang == "markdown":
        identifiers.update(re.findall(r"^#+\s+(.*)", content, re.MULTILINE))

    return list(identifiers)
