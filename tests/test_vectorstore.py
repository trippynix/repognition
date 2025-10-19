import unittest
from unittest.mock import patch, MagicMock
import os
from src.components.vectorstore import VectorstoreManager

class TestVectorstoreManager(unittest.TestCase):
    @patch("src.components.vectorstore.OllamaEmbeddings")
    @patch("src.components.vectorstore.FAISS")
    def test_create_vectorstore(self, mock_faiss, mock_embeddings):
        manager = VectorstoreManager()
        chunks = [{"content": "content", "summary": "summary", "keywords": "keywords"}]
        
        # Mock the embedding dimension
        mock_embeddings.return_value.embed_query.return_value = [0.1] * 10
        
        manager.create_vectorstore(chunks)
        self.assertTrue(mock_faiss.called)

    @patch("src.components.vectorstore.FAISS")
    @patch("os.path.exists")
    def test_save_and_load(self, mock_exists, mock_faiss):
        # Ensure os.path.exists returns True for the load operation
        mock_exists.return_value = True
        
        manager = VectorstoreManager()
        mock_vectorstore = MagicMock()
        
        db_path = os.path.join(manager.db_path, "repo_vectorstore")
        
        # Test save
        manager.save(mock_vectorstore, "repo")
        mock_vectorstore.save_local.assert_called_with(db_path)
        
        # Test load
        manager.load("repo")
        mock_faiss.load_local.assert_called_with(
            db_path, manager.embeddings, allow_dangerous_deserialization=True
        )

if __name__ == '__main__':
    unittest.main()