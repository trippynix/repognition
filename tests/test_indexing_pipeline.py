import unittest
from unittest.mock import patch
from src.pipeline.indexing import IndexingPipeline

class TestIndexingPipeline(unittest.TestCase):
    @patch("src.pipeline.indexing.clone_github_repo")
    @patch("src.pipeline.indexing.process_and_chunk_file")
    @patch("src.pipeline.indexing.VectorstoreManager")
    def test_run(self, mock_manager, mock_process, mock_clone):
        mock_manager.return_value.load.return_value = None
        mock_clone.return_value = "repo_path"
        mock_process.return_value = [{"content": "chunk"}]
        
        pipeline = IndexingPipeline("https://github.com/user/repo")
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [("root", ["dirs"], ["file.py"])]
            pipeline.run()
        
        self.assertTrue(mock_manager.return_value.create_vectorstore.called)
        self.assertTrue(mock_manager.return_value.save.called)

if __name__ == "__main__":
    unittest.main()