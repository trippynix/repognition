import os
import unittest
from unittest.mock import patch, MagicMock
from src.components.git_cloner import clone_github_repo

class TestGitCloner(unittest.TestCase):
    @patch("src.components.git_cloner.Repo")
    @patch("os.path.exists")
    def test_clone_github_repo_new(self, mock_exists, mock_repo):
        mock_exists.return_value = False
        github_url = "https://github.com/user/repo"
        local_path = os.path.join("repos", "repo")
        clone_github_repo(github_url, "repos")
        mock_repo.clone_from.assert_called_once_with(github_url, local_path)

    @patch("src.components.git_cloner.Repo")
    @patch("os.path.exists")
    def test_clone_github_repo_existing(self, mock_exists, mock_repo):
        mock_exists.return_value = True
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        github_url = "https://github.com/user/repo"
        clone_github_repo(github_url, "repos")
        mock_repo_instance.remotes.origin.pull.assert_called_once()

if __name__ == "__main__":
    unittest.main()