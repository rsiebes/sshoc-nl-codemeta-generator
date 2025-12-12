"""
Unit tests for codemeta_readme module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_readme


class TestReadmeExtraction(unittest.TestCase):
    """Test README extraction."""

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_basic_readme_extraction(self, mock_fetch):
        """Test extraction of basic README content."""
        mock_fetch.return_value = "# My Project\n\nThis is a test project."
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], "# My Project\n\nThis is a test project.")

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_md_priority(self, mock_fetch):
        """Test that README.md has priority."""
        mock_fetch.return_value = "# README.md content"
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], "# README.md content")

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_rst_fallback(self, mock_fetch):
        """Test fallback to README.rst."""
        # First call returns None (README.md not found)
        # Second call returns README.rst content
        mock_fetch.side_effect = [None, "README.rst content"]
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], "README.rst content")

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_txt_fallback(self, mock_fetch):
        """Test fallback to README.txt."""
        # First two calls return None, third returns README.txt content
        mock_fetch.side_effect = [None, None, "README.txt content"]
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], "README.txt content")

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_no_extension_fallback(self, mock_fetch):
        """Test fallback to README (no extension)."""
        # First three calls return None, fourth returns README content
        mock_fetch.side_effect = [None, None, None, "README content"]
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], "README content")

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_missing_readme(self, mock_fetch):
        """Test handling of missing README."""
        mock_fetch.return_value = None
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_api_error_handling(self, mock_fetch):
        """Test handling of API errors."""
        mock_fetch.side_effect = Exception("API Error")
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_readme.get("invalid-url")
        
        self.assertEqual(result, {})


class TestReadmeContent(unittest.TestCase):
    """Test README content validation."""

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_is_string(self, mock_fetch):
        """Test that README content is a string."""
        mock_fetch.return_value = "# Project"
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertIsInstance(result["readme"], str)

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_not_empty(self, mock_fetch):
        """Test that README content is not empty."""
        mock_fetch.return_value = "# Project"
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertTrue(result["readme"])

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_with_markdown_formatting(self, mock_fetch):
        """Test README with markdown formatting."""
        content = """# Project Title

## Description
This is a test project.

## Installation
```bash
pip install project
```

## Usage
See documentation.
"""
        mock_fetch.return_value = content
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], content)

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_readme_with_special_characters(self, mock_fetch):
        """Test README with special characters."""
        content = "# Project\n\nSpecial chars: é, ñ, ü, 中文"
        mock_fetch.return_value = content
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], content)


class TestRealRepositories(unittest.TestCase):
    """Test README extraction from real repositories."""

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_tensorflow_readme(self, mock_fetch):
        """Test README extraction from TensorFlow."""
        mock_fetch.return_value = "# TensorFlow\n\nAn Open Source Machine Learning Framework"
        result = codemeta_readme.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("readme", result)
        self.assertTrue(result["readme"].startswith("# TensorFlow"))

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_flask_readme(self, mock_fetch):
        """Test README extraction from Flask."""
        mock_fetch.return_value = "# Flask\n\nThe Python micro framework for building web applications"
        result = codemeta_readme.get("https://github.com/pallets/flask")
        
        self.assertIn("readme", result)
        self.assertTrue(result["readme"].startswith("# Flask"))

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_rust_readme(self, mock_fetch):
        """Test README extraction from Rust."""
        mock_fetch.return_value = "# The Rust Programming Language"
        result = codemeta_readme.get("https://github.com/rust-lang/rust")
        
        self.assertIn("readme", result)
        self.assertTrue(result["readme"].startswith("# The Rust"))


class TestReadmeURL(unittest.TestCase):
    """Test README URL generation."""

    def test_readme_url_format(self):
        """Test that README URL is constructed correctly."""
        url = codemeta_readme.get_readme_url("owner", "repo")
        
        self.assertEqual(url, "https://raw.githubusercontent.com/owner/repo/main/README.md")

    def test_readme_url_with_special_names(self):
        """Test README URL with special characters in names."""
        url = codemeta_readme.get_readme_url("owner-name", "repo-name")
        
        self.assertEqual(url, "https://raw.githubusercontent.com/owner-name/repo-name/main/README.md")

    def test_readme_url_with_numbers(self):
        """Test README URL with numbers in names."""
        url = codemeta_readme.get_readme_url("owner123", "repo456")
        
        self.assertEqual(url, "https://raw.githubusercontent.com/owner123/repo456/main/README.md")


class TestReadmeFallback(unittest.TestCase):
    """Test README file format fallback."""

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_all_readme_formats_tried(self, mock_fetch):
        """Test that all README formats are tried."""
        # All return None - should try all formats
        mock_fetch.return_value = None
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})
        # Should have been called 4 times (README.md, README.rst, README.txt, README)
        self.assertEqual(mock_fetch.call_count, 4)

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_stops_at_first_found(self, mock_fetch):
        """Test that search stops at first found README."""
        mock_fetch.return_value = "# README.md"
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        # Should only be called once (found README.md)
        self.assertEqual(mock_fetch.call_count, 1)


class TestReadmeSize(unittest.TestCase):
    """Test README content size handling."""

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_small_readme(self, mock_fetch):
        """Test small README content."""
        mock_fetch.return_value = "# Small"
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(len(result["readme"]), 7)

    @patch('src.modules.codemeta_readme.fetch_file_content')
    def test_large_readme(self, mock_fetch):
        """Test large README content."""
        large_content = "# Large\n" + "\n".join(["Line " + str(i) for i in range(1000)])
        mock_fetch.return_value = large_content
        result = codemeta_readme.get("https://github.com/owner/repo")
        
        self.assertIn("readme", result)
        self.assertEqual(result["readme"], large_content)


if __name__ == '__main__':
    unittest.main()
