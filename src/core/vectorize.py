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
    def _create_vectorstore(self, dim):
        """Initialize empty FAISS vectorstore."""
        index = faiss.IndexFlatL2(dim)
        return FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

    # -----------------------------
    # SAVE / LOAD VECTORSTORE
    # -----------------------------
    def save(self):
        """Save FAISS index + metadata."""
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        faiss.write_index(
            self.vectorstore.index, os.path.join(self.db_path, "index.faiss")
        )
        with open(os.path.join(self.db_path, "docstore.pkl"), "wb") as f:
            pickle.dump(
                (self.vectorstore.docstore, self.vectorstore.index_to_docstore_id), f
            )

    def load(self):
        """Load existing FAISS index + metadata."""
        index = faiss.read_index(os.path.join(self.db_path, "index.faiss"))
        with open(os.path.join(self.db_path, "docstore.pkl"), "rb") as f:
            docstore, index_to_docstore_id = pickle.load(f)

        self.vectorstore = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )
        return self.vectorstore

    # -----------------------------
    # BUILD VECTORSTORE
    # -----------------------------
    def build(self):
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

        # Generate embeddings for the first text to determine dimension
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query(texts[0])))

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
