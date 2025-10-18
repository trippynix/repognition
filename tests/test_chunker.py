import unittest
from unittest.mock import patch
from src.components.chunker import process_and_chunk_file

class TestChunker(unittest.TestCase):
    @patch("src.components.chunker.generate_summary")
    @patch("src.components.chunker.extract_keywords")
    @patch("src.components.chunker._parse_file")
    def test_process_and_chunk_file(self, mock_parse, mock_keywords, mock_summary):
        mock_parse.return_value = ([{"content": "def hello(): pass", "start_line": 1, "end_line": 1}], "python")
        mock_summary.return_value = "A summary"
        mock_keywords.return_value = "hello"
        
        chunks = process_and_chunk_file("test.py", "test_repo")
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['repo'], 'test_repo')
        self.assertEqual(chunks[0]['summary'], 'A summary')
        self.assertEqual(chunks[0]['keywords'], 'hello')

if __name__ == '__main__':
    unittest.main()