from langchain_text_splitters import MarkdownHeaderTextSplitter


def markdown_split(content):
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    )
    docs = markdown_splitter.split_text(content)
    return [doc.page_content for doc in docs]
