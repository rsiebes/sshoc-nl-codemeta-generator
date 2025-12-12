"""
Unit tests for codemeta_code_repository module.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.modules import codemeta_code_repository


class TestCodeRepositoryExtraction(unittest.TestCase):
    """Test code repository extraction."""

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_basic_repository_extraction(self, mock_fetch):
        """Test extraction of basic repository information."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git",
            "ssh_url": "git@github.com:owner/repo.git",
            "language": "Python",
            "size": 1024,
            "private": False,
            "fork": False,
            "default_branch": "main"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["@type"], "Repository")
        self.assertEqual(repo["url"], "https://github.com/owner/repo")
        self.assertEqual(repo["language"], "Python")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_with_clone_url(self, mock_fetch):
        """Test extraction of repository with clone URL."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/tensorflow/tensorflow.git",
            "language": "C++",
            "private": False,
            "fork": False
        }
        result = codemeta_code_repository.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["clone_url"], "https://github.com/tensorflow/tensorflow.git")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_private_repository(self, mock_fetch):
        """Test extraction of private repository information."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/private-repo.git",
            "private": True,
            "fork": False
        }
        result = codemeta_code_repository.get("https://github.com/owner/private-repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertTrue(repo["private"])

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_forked_repository(self, mock_fetch):
        """Test extraction of forked repository information."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/forked-repo.git",
            "private": False,
            "fork": True,
            "language": "JavaScript"
        }
        result = codemeta_code_repository.get("https://github.com/owner/forked-repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertTrue(repo["fork"])

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_with_ssh_url(self, mock_fetch):
        """Test extraction of repository with SSH URL."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git",
            "ssh_url": "git@github.com:owner/repo.git",
            "language": "Python"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["ssh_url"], "git@github.com:owner/repo.git")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_with_size(self, mock_fetch):
        """Test extraction of repository with size information."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git",
            "size": 5120,
            "language": "Python"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["size"], 5120)

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_with_default_branch(self, mock_fetch):
        """Test extraction of repository with default branch."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git",
            "default_branch": "develop",
            "language": "Python"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["default_branch"], "develop")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_minimal_repository_info(self, mock_fetch):
        """Test extraction with minimal repository information."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["@type"], "Repository")
        self.assertEqual(repo["url"], "https://github.com/owner/repo")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_missing_repository_info(self, mock_fetch):
        """Test handling of missing repository information."""
        mock_fetch.return_value = None
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_api_error_handling(self, mock_fetch):
        """Test handling of API errors."""
        mock_fetch.side_effect = Exception("API Error")
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_code_repository.get("invalid-url")
        
        self.assertEqual(result, {})


class TestRepositoryContent(unittest.TestCase):
    """Test code repository content validation."""

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_has_type(self, mock_fetch):
        """Test that repository has @type field."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        self.assertIn("@type", result["codeRepository"])
        self.assertEqual(result["codeRepository"]["@type"], "Repository")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_has_url(self, mock_fetch):
        """Test that repository has URL field."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        self.assertIn("url", result["codeRepository"])

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_url_is_string(self, mock_fetch):
        """Test that repository URL is a string."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        self.assertIsInstance(result["codeRepository"]["url"], str)

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_repository_type_is_repository(self, mock_fetch):
        """Test that repository type is 'Repository'."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/repo.git"
        }
        result = codemeta_code_repository.get("https://github.com/owner/repo")
        
        self.assertIn("codeRepository", result)
        self.assertEqual(result["codeRepository"]["@type"], "Repository")


class TestRealRepositories(unittest.TestCase):
    """Test code repository extraction from real repositories."""

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_tensorflow_repository(self, mock_fetch):
        """Test code repository extraction from TensorFlow."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/tensorflow/tensorflow.git",
            "ssh_url": "git@github.com:tensorflow/tensorflow.git",
            "language": "C++",
            "size": 1024000,
            "private": False,
            "fork": False,
            "default_branch": "master"
        }
        result = codemeta_code_repository.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["@type"], "Repository")
        self.assertEqual(repo["language"], "C++")
        self.assertFalse(repo["private"])

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_flask_repository(self, mock_fetch):
        """Test code repository extraction from Flask."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/pallets/flask.git",
            "ssh_url": "git@github.com:pallets/flask.git",
            "language": "Python",
            "size": 2048,
            "private": False,
            "fork": False,
            "default_branch": "main"
        }
        result = codemeta_code_repository.get("https://github.com/pallets/flask")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["language"], "Python")
        self.assertEqual(repo["default_branch"], "main")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_rust_repository(self, mock_fetch):
        """Test code repository extraction from Rust."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/rust-lang/rust.git",
            "ssh_url": "git@github.com:rust-lang/rust.git",
            "language": "Rust",
            "size": 512000,
            "private": False,
            "fork": False,
            "default_branch": "master"
        }
        result = codemeta_code_repository.get("https://github.com/rust-lang/rust")
        
        self.assertIn("codeRepository", result)
        repo = result["codeRepository"]
        self.assertEqual(repo["language"], "Rust")
        self.assertFalse(repo["fork"])


class TestRepositoryTypes(unittest.TestCase):
    """Test different repository types."""

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_python_repository(self, mock_fetch):
        """Test Python repository detection."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/python-project.git",
            "language": "Python"
        }
        result = codemeta_code_repository.get("https://github.com/owner/python-project")
        
        self.assertIn("codeRepository", result)
        self.assertEqual(result["codeRepository"]["language"], "Python")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_javascript_repository(self, mock_fetch):
        """Test JavaScript repository detection."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/js-project.git",
            "language": "JavaScript"
        }
        result = codemeta_code_repository.get("https://github.com/owner/js-project")
        
        self.assertIn("codeRepository", result)
        self.assertEqual(result["codeRepository"]["language"], "JavaScript")

    @patch('src.modules.codemeta_code_repository.fetch_repository_info')
    def test_java_repository(self, mock_fetch):
        """Test Java repository detection."""
        mock_fetch.return_value = {
            "clone_url": "https://github.com/owner/java-project.git",
            "language": "Java"
        }
        result = codemeta_code_repository.get("https://github.com/owner/java-project")
        
        self.assertIn("codeRepository", result)
        self.assertEqual(result["codeRepository"]["language"], "Java")


if __name__ == '__main__':
    unittest.main()
