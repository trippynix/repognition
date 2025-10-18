import unittest
from unittest.mock import patch, MagicMock
from src.llm.ollama_client import stream_ollama_response, generate_summary, extract_keywords

class TestOllamaClient(unittest.TestCase):
    @patch("requests.post")
    def test_stream_ollama_response_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [b'{"message": {"content": "response"}}']
        mock_post.return_value = mock_response

        response = stream_ollama_response("prompt")
        self.assertEqual(response, "response")

    @patch("requests.post")
    def test_stream_ollama_response_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        response = stream_ollama_response("prompt")
        self.assertEqual(response, "[Ollama error 500: Internal Server Error]")

    @patch("src.llm.ollama_client.stream_ollama_response")
    def test_generate_summary(self, mock_stream):
        mock_stream.return_value = "summary"
        summary = generate_summary("code")
        self.assertEqual(summary, "summary")

    @patch("src.llm.ollama_client.stream_ollama_response")
    def test_extract_keywords(self, mock_stream):
        mock_stream.return_value = "keywords"
        keywords = extract_keywords("code")
        self.assertEqual(keywords, "keywords")

if __name__ == '__main__':
    unittest.main()