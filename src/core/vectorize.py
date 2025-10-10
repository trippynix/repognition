# vectorize.py
import os
import json
import pickle
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from uuid import uuid4


class Vectorizer:
    def __init__(
        self,
        chunks_path="data/chunks.json",
        db_path="data/vectorstore",
        embedding_model="nomic-embed-text",
    ):
        self.chunks_path = chunks_path
        self.db_path = db_path
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.vectorstore = None

    # -----------------------------
    # VECTORSTORE CREATION
    # -----------------------------
    def _create_vectorstore(self, dim, texts, metadatas):
        """Initialize empty FAISS vectorstore."""
        # Generate embeddings for the first text to determine dimension
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query(dim)))

        # Generate embeddings
        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]
        uuids = [str(uuid4()) for _ in range(len(texts))]

        vector_store.add_documents(documents=docs, ids=uuids)
        return vector_store

    # -----------------------------
    # SAVE / LOAD VECTORSTORE
    # -----------------------------
    def save(self, vector_store, github_url):
        """Save FAISS index + metadata."""
        vector_store.save_local(
            os.path.join(self.db_path, f"{github_url.split('/')[-1]}_vectorstore")
        )

    def load(self, github_url):
        """Load existing FAISS index + metadata."""
        path = os.path.join(self.db_path, f"{github_url.split('/')[-1]}_vectorstore")
        vectorstore = FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True
        )

        return vectorstore

    # -----------------------------
    # BUILD VECTORSTORE
    # -----------------------------
    def build(self, github_url):
        """Build FAISS vectorstore from chunks JSON."""
        if not os.path.exists(self.chunks_path):
            raise FileNotFoundError(f"Chunks file not found: {self.chunks_path}")

        with open(self.chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        if not chunks:
            raise ValueError("No chunks found in JSON.")

        # Extract texts and metadata (without content to avoid duplication)
        texts = [c["content"] + c["summary"] + c["keywords"] for c in chunks]
        metadatas = [{k: v for k, v in c.items() if k != "content"} for c in chunks]

        # Dimension of embeddings
        dim = len(self.embeddings.embed_query(texts[0]))

        vector_store = self._create_vectorstore(dim, texts, metadatas)

        self.save(vector_store, github_url)

        return vector_store


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    vectorizer = Vectorizer()

    if os.path.exists(os.path.join(vectorizer.db_path, "index.faiss")):
        print("🔄 Loading existing FAISS vectorstore...")
        vectorizer.load()
    else:
        print("⚡ Creating new FAISS vectorstore...")
        vectorizer.build()
