import unittest
from unittest.mock import patch
from src.components.chunker import process_and_chunk_file


class TestChunker(unittest.TestCase):

    # We now only need to patch 'enrich_chunk'
    @patch("src.components.chunker.enrich_chunk")
    @patch("src.components.chunker._parse_file")
    def test_process_and_chunk_file(self, mock_parse, mock_enrich):
        # 1. Setup the mocks
        # Mock the file parser to return a simple code chunk
        mock_parse.return_value = (
            [
                {
                    "content": "def hello(): pass",
                    "start_line": 1,
                    "end_line": 1,
                    "type": "function",
                }
            ],
            "python",
        )

        # Mock the enrich_chunk function to return a predefined dictionary
        mock_enrich.return_value = {
            "summary": "A test summary",
            "keywords": "test, keywords",
        }

        # 2. Call the function we are testing
        chunks = process_and_chunk_file("test.py", "test_repo")

        # 3. Assert the results
        self.assertEqual(len(chunks), 1)
        chunk = chunks[0]
        self.assertEqual(chunk["repo"], "test_repo")
        self.assertEqual(chunk["summary"], "A test summary")
        self.assertEqual(chunk["keywords"], "test, keywords")

        # Verify that our mocks were called as expected
        mock_parse.assert_called_once_with("test.py")
        mock_enrich.assert_called_once_with("def hello(): pass")


if __name__ == "__main__":
    unittest.main()
