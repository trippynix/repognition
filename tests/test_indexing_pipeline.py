import unittest
from unittest.mock import patch, MagicMock
from src.pipeline.indexing import IndexingPipeline


class TestIndexingPipeline(unittest.TestCase):

    # We need to patch all the external dependencies of the 'run' method
    @patch("src.pipeline.indexing.clone_github_repo")
    @patch("src.pipeline.indexing.load_cache")
    @patch("src.pipeline.indexing.calculate_file_hash")
    @patch("src.pipeline.indexing.Pool")  # To mock the multiprocessing pool
    @patch("src.pipeline.indexing.VectorstoreManager")
    @patch("src.pipeline.indexing.save_cache")
    @patch("os.path.exists")
    @patch("builtins.open")
    def test_run_with_new_files(
        self,
        mock_open,
        mock_exists,
        mock_save_cache,
        mock_manager,
        mock_pool,
        mock_hash,
        mock_load_cache,
        mock_clone,
    ):
        # 1. --- Setup Mocks ---

        # Simulate an empty cache, as if it's the first run
        mock_load_cache.return_value = {}

        # Simulate finding one new file
        mock_hash.return_value = "new_file_hash"

        # Mock the file system and repo cloning
        mock_clone.return_value = "repo_path"
        mock_exists.return_value = False  # No existing chunks file

        # Mock the multiprocessing pool to return some processed chunks
        mock_pool.return_value.__enter__.return_value.map.return_value = [
            ("repo_path/file.py", [{"chunk_id": "file.py-0", "content": "chunk"}])
        ]

        # Mock the vector store manager
        mock_vs_manager_instance = mock_manager.return_value
        mock_vs_manager_instance.load.return_value = None  # No existing vector store

        # 2. --- Call the Method ---
        pipeline = IndexingPipeline("https://github.com/fake/repo")
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [("repo_path", [], ["file.py"])]
            pipeline.run()

        # 3. --- Assert Results ---

        # Check that it tried to load the cache and clone the repo
        mock_load_cache.assert_called_once_with("repo")
        mock_clone.assert_called_once()

        # Check that since it's a new run, it created a new vector store
        mock_vs_manager_instance.create_vectorstore.assert_called_once()

        # Check that it saved the new vector store and the new cache
        mock_vs_manager_instance.save.assert_called_once()
        mock_save_cache.assert_called_once()


if __name__ == "__main__":
    unittest.main()
