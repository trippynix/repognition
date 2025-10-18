import unittest
from unittest.mock import patch, MagicMock
from src.pipeline.querying import QueryPipeline

class TestQueryPipeline(unittest.TestCase):
    @patch("src.pipeline.querying.VectorstoreManager")
    @patch("src.pipeline.querying.RetrievalQA")
    def test_setup(self, mock_qa, mock_manager):
        mock_manager.return_value.load.return_value = MagicMock()
        pipeline = QueryPipeline("https://github.com/user/repo")
        pipeline.setup()
        self.assertTrue(mock_qa.from_chain_type.called)

    @patch("src.pipeline.querying.VectorstoreManager")
    def test_ask(self, mock_manager):
        pipeline = QueryPipeline("https://github.com/user/repo")
        pipeline.qa_chain = MagicMock()
        pipeline.ask("question")
        self.assertTrue(pipeline.qa_chain.invoke.called)

if __name__ == "__main__":
    unittest.main()