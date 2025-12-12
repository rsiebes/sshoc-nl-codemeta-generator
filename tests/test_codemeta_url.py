"""
Unit tests for codemeta_url module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_url


class TestURLValidation(unittest.TestCase):
    """Test URL validation."""

    def test_valid_https_url(self):
        """Test validation of valid HTTPS URL."""
        self.assertTrue(codemeta_url.validate_url("https://example.com"))

    def test_valid_http_url(self):
        """Test validation of valid HTTP URL."""
        self.assertTrue(codemeta_url.validate_url("http://example.com"))

    def test_invalid_url_no_protocol(self):
        """Test validation of URL without protocol."""
        self.assertFalse(codemeta_url.validate_url("example.com"))

    def test_invalid_url_empty(self):
        """Test validation of empty URL."""
        self.assertFalse(codemeta_url.validate_url(""))

    def test_invalid_url_none(self):
        """Test validation of None URL."""
        self.assertFalse(codemeta_url.validate_url(None))

    def test_invalid_url_too_short(self):
        """Test validation of too short URL."""
        self.assertFalse(codemeta_url.validate_url("http://a"))

    def test_valid_url_with_path(self):
        """Test validation of URL with path."""
        self.assertTrue(codemeta_url.validate_url("https://example.com/path"))

    def test_valid_url_with_query(self):
        """Test validation of URL with query parameters."""
        self.assertTrue(codemeta_url.validate_url("https://example.com?param=value"))


class TestURLExtraction(unittest.TestCase):
    """Test URL extraction."""

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_from_repository_info(self, mock_fetch):
        """Test extraction of URL from repository info."""
        mock_fetch.return_value = {
            "homepage": "https://example.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://example.com")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_from_repository_info_http(self, mock_fetch):
        """Test extraction of HTTP URL from repository info."""
        mock_fetch.return_value = {
            "homepage": "http://example.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "http://example.com")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_missing_url(self, mock_fetch):
        """Test handling of missing URL."""
        mock_fetch.return_value = {}
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_invalid_url_in_repository_info(self, mock_fetch):
        """Test handling of invalid URL in repository info."""
        mock_fetch.return_value = {
            "homepage": "not-a-url"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_none_repository_info(self, mock_fetch):
        """Test handling of None repository info."""
        mock_fetch.return_value = None
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_api_error_handling(self, mock_fetch):
        """Test handling of API errors."""
        mock_fetch.side_effect = Exception("API Error")
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_url.get("invalid-url")
        
        self.assertEqual(result, {})


class TestURLContent(unittest.TestCase):
    """Test URL content validation."""

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_is_string(self, mock_fetch):
        """Test that URL is a string."""
        mock_fetch.return_value = {
            "homepage": "https://example.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertIsInstance(result["url"], str)

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_not_empty(self, mock_fetch):
        """Test that URL is not empty."""
        mock_fetch.return_value = {
            "homepage": "https://example.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertTrue(result["url"])

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_starts_with_http(self, mock_fetch):
        """Test that URL starts with http or https."""
        mock_fetch.return_value = {
            "homepage": "https://example.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertTrue(result["url"].startswith("http"))


class TestRealRepositories(unittest.TestCase):
    """Test URL extraction from real repositories."""

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_tensorflow_url(self, mock_fetch):
        """Test URL extraction from TensorFlow."""
        mock_fetch.return_value = {
            "homepage": "https://www.tensorflow.org"
        }
        result = codemeta_url.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://www.tensorflow.org")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_flask_url(self, mock_fetch):
        """Test URL extraction from Flask."""
        mock_fetch.return_value = {
            "homepage": "https://flask.palletsprojects.com"
        }
        result = codemeta_url.get("https://github.com/pallets/flask")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://flask.palletsprojects.com")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_rust_url(self, mock_fetch):
        """Test URL extraction from Rust."""
        mock_fetch.return_value = {
            "homepage": "https://www.rust-lang.org"
        }
        result = codemeta_url.get("https://github.com/rust-lang/rust")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://www.rust-lang.org")


class TestURLFromReadme(unittest.TestCase):
    """Test URL extraction from README."""

    @patch('src.modules.codemeta_url.fetch_repository_info')
    @patch('src.modules.codemeta_url.fetch_file_content')
    def test_url_from_readme_markdown_link(self, mock_file, mock_fetch):
        """Test extraction of URL from README markdown link."""
        mock_fetch.return_value = {}
        mock_file.return_value = "[Homepage](https://example.com)"
        
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://example.com")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    @patch('src.modules.codemeta_url.fetch_file_content')
    def test_url_from_readme_website_link(self, mock_file, mock_fetch):
        """Test extraction of website URL from README."""
        mock_fetch.return_value = {}
        mock_file.return_value = "[Official Website](https://myproject.io)"
        
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://myproject.io")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    @patch('src.modules.codemeta_url.fetch_file_content')
    def test_url_from_readme_direct_url(self, mock_file, mock_fetch):
        """Test extraction of direct URL from README."""
        mock_fetch.return_value = {}
        mock_file.return_value = "Visit https://example.com for more information"
        
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://example.com")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    @patch('src.modules.codemeta_url.fetch_file_content')
    def test_url_from_readme_prefers_non_github(self, mock_file, mock_fetch):
        """Test that non-GitHub URLs are preferred."""
        mock_fetch.return_value = {}
        mock_file.return_value = "https://github.com/owner/repo and https://example.com"
        
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        # Should prefer the non-GitHub URL
        self.assertEqual(result["url"], "https://example.com")


class TestURLPriority(unittest.TestCase):
    """Test URL extraction priority."""

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_repository_info_priority(self, mock_fetch):
        """Test that repository info URL has priority."""
        mock_fetch.return_value = {
            "homepage": "https://official.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://official.com")


class TestURLFormats(unittest.TestCase):
    """Test different URL formats."""

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_with_subdomain(self, mock_fetch):
        """Test URL with subdomain."""
        mock_fetch.return_value = {
            "homepage": "https://docs.example.com"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://docs.example.com")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_with_path(self, mock_fetch):
        """Test URL with path."""
        mock_fetch.return_value = {
            "homepage": "https://example.com/project"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://example.com/project")

    @patch('src.modules.codemeta_url.fetch_repository_info')
    def test_url_with_port(self, mock_fetch):
        """Test URL with port."""
        mock_fetch.return_value = {
            "homepage": "https://example.com:8080"
        }
        result = codemeta_url.get("https://github.com/owner/repo")
        
        self.assertIn("url", result)
        self.assertEqual(result["url"], "https://example.com:8080")


if __name__ == '__main__':
    unittest.main()
