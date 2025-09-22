from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def markdown_split(content):
    """Split markdown into chunks with metadata (headers + line numbers)."""
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    )
    docs = markdown_splitter.split_text(content)

    chunks = []
    last_index = 0  # track processed content

    for doc in docs:
        chunk_text = doc.page_content
        start_index = content.find(
            chunk_text, last_index
        )  # find from last_index forward
        if start_index == -1:
            continue  # skip if not found

        start_line = content[:start_index].count("\n") + 1
        end_line = start_line + chunk_text.count("\n")

        chunks.append(
            {
                "content": chunk_text,
                "metadata": doc.metadata,  # keeps header info
                "start_line": start_line,
                "end_line": end_line,
            }
        )

        last_index = start_index + len(chunk_text)

    # Optional fallback: capture leftover content not split by headers
    if last_index < len(content):
        leftovers = content[last_index:]
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        for chunk in splitter.split_text(leftovers):
            chunks.append(
                {
                    "content": chunk,
                    "metadata": {"header": "Unstructured"},
                    "start_line": None,
                    "end_line": None,
                }
            )

    return chunks
