import unittest
import json
from unittest.mock import patch, MagicMock
import requests

from src.llm.ollama_client import enrich_chunk


class TestOllamaClient(unittest.TestCase):

    @patch("requests.post")
    def test_enrich_chunk_success(self, mock_post):
        """
        Tests that enrich_chunk successfully parses a valid JSON response from Ollama.
        """
        mock_response_content = {
            "summary": "This is a test summary.",
            "keywords": "test, summary, keywords",
        }
        mock_ollama_response = {
            "message": {"content": json.dumps(mock_response_content)}
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ollama_response
        mock_post.return_value = mock_response

        result = enrich_chunk("some code chunk")
        self.assertEqual(result, mock_response_content)

    @patch("requests.post")
    def test_enrich_chunk_http_error_returns_default(self, mock_post):
        """
        Tests that enrich_chunk returns an empty default dict on an HTTP error.
        """
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = enrich_chunk("some code chunk")
        self.assertEqual(result, {"summary": "", "keywords": ""})

    @patch("requests.post")
    def test_enrich_chunk_network_error_returns_default(self, mock_post):
        """
        Tests that enrich_chunk returns an empty default dict on a network connection error.
        """
        mock_post.side_effect = requests.exceptions.RequestException

        result = enrich_chunk("some code chunk")
        self.assertEqual(result, {"summary": "", "keywords": ""})


if __name__ == "__main__":
    unittest.main()
