# src/components/vectorstore.py
import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from uuid import uuid4
from config.settings import VECTORSTORE_PATH, EMBEDDING_MODEL


class VectorstoreManager:
    def __init__(self):
        self.db_path = VECTORSTORE_PATH
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    def create_vectorstore(self, chunks):
        """Creates and returns a new FAISS vectorstore from chunks."""
        # --- START OF FIX ---
        texts = []
        for c in chunks:
            # Ensure keywords is a string before concatenation
            keywords = c.get("keywords", "")
            if isinstance(keywords, list):
                keywords = ", ".join(keywords)  # Join list into a string

            # Combine all text content
            full_text = c.get("content", "") + c.get("summary", "") + keywords
            texts.append(full_text)

        metadatas = [{k: v for k, v in c.items() if k != "content"} for c in chunks]

        docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]
        uuids = [str(uuid4()) for _ in texts]

        # Initialize an empty FAISS index
        embedding_dim = len(self.embeddings.embed_query(texts[0]))
        index = faiss.IndexFlatL2(embedding_dim)

        vectorstore = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        vectorstore.add_documents(documents=docs, ids=uuids)
        return vectorstore

    def add_documents(self, vectorstore, chunks):
        """Adds new documents to an existing vectorstore."""
        texts = []
        for c in chunks:
            keywords = c.get("keywords", "")
            if isinstance(keywords, list):
                keywords = ", ".join(keywords)
            full_text = c.get("content", "") + c.get("summary", "") + keywords
            texts.append(full_text)

        metadatas = [{k: v for k, v in c.items() if k != "content"} for c in chunks]
        docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]
        uuids = [c["chunk_id"] for c in chunks]  # Use our custom chunk_id

        vectorstore.add_documents(documents=docs, ids=uuids)
        return vectorstore

    def delete(self, vectorstore, chunk_ids):
        """
        Deletes documents from the vectorstore by their chunk_id,
        safely ignoring any IDs that are not found.
        """
        if not vectorstore or not chunk_ids:
            return vectorstore

        # Find which of the requested IDs actually exist in the vector store
        ids_to_delete = [
            id_ for id_ in chunk_ids if id_ in vectorstore.index_to_docstore_id.values()
        ]

        if ids_to_delete:
            vectorstore.delete(ids=ids_to_delete)

        return vectorstore

    def save(self, vectorstore, repo_name):
        """Saves a FAISS vectorstore."""
        path = os.path.join(self.db_path, f"{repo_name}_vectorstore")
        vectorstore.save_local(path)
        print(f"Vectorstore saved to {path}")

    def load(self, repo_name):
        """Loads an existing FAISS vectorstore."""
        path = os.path.join(self.db_path, f"{repo_name}_vectorstore")
        if not os.path.exists(path):
            return None
        return FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True
        )
