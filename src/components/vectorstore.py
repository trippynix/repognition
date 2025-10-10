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
        texts = [c["content"] + c["summary"] + c["keywords"] for c in chunks]
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
