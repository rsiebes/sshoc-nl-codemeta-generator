"""
Unit tests for codemeta_date_created module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_date_created


class TestDateCreatedExtraction(unittest.TestCase):
    """Test creation date extraction."""

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_basic_date_extraction(self, mock_fetch):
        """Test extraction of basic creation date."""
        mock_fetch.return_value = {
            "created_at": "2020-01-15T10:30:45Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2020-01-15")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_date_format_conversion(self, mock_fetch):
        """Test conversion of GitHub date format to ISO 8601."""
        mock_fetch.return_value = {
            "created_at": "2022-07-12T18:34:47Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2022-07-12")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_recent_date(self, mock_fetch):
        """Test extraction of recent creation date."""
        mock_fetch.return_value = {
            "created_at": "2025-12-01T12:00:00Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2025-12-01")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_old_date(self, mock_fetch):
        """Test extraction of old creation date."""
        mock_fetch.return_value = {
            "created_at": "2010-06-30T12:34:56Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2010-06-30")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_missing_creation_date(self, mock_fetch):
        """Test handling of missing creation date."""
        mock_fetch.return_value = {}
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_none_repository_info(self, mock_fetch):
        """Test handling of None repository info."""
        mock_fetch.return_value = None
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_api_error_handling(self, mock_fetch):
        """Test handling of API errors."""
        mock_fetch.side_effect = Exception("API Error")
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_date_created.get("invalid-url")
        
        self.assertEqual(result, {})


class TestDateContent(unittest.TestCase):
    """Test creation date content validation."""

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_date_is_string(self, mock_fetch):
        """Test that creation date is a string."""
        mock_fetch.return_value = {
            "created_at": "2020-01-15T10:30:45Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertIsInstance(result["dateCreated"], str)

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_date_not_empty(self, mock_fetch):
        """Test that creation date is not empty."""
        mock_fetch.return_value = {
            "created_at": "2020-01-15T10:30:45Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertTrue(result["dateCreated"])

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_date_format_iso8601(self, mock_fetch):
        """Test that creation date is in ISO 8601 format."""
        mock_fetch.return_value = {
            "created_at": "2020-01-15T10:30:45Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        date_str = result["dateCreated"]
        # Check format YYYY-MM-DD
        self.assertRegex(date_str, r'^\d{4}-\d{2}-\d{2}$')

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_date_valid_range(self, mock_fetch):
        """Test that creation date is in valid range."""
        mock_fetch.return_value = {
            "created_at": "2020-01-15T10:30:45Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        date_str = result["dateCreated"]
        # Parse and validate
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # Check it's a reasonable date (after GitHub was founded in 2008)
            self.assertGreaterEqual(date_obj.year, 2008)
            # Check it's not in the future
            self.assertLessEqual(date_obj.year, 2100)
        except ValueError:
            self.fail("Date is not in valid ISO 8601 format")


class TestRealRepositories(unittest.TestCase):
    """Test creation date extraction from real repositories."""

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_tensorflow_creation_date(self, mock_fetch):
        """Test creation date extraction from TensorFlow."""
        mock_fetch.return_value = {
            "created_at": "2015-11-09T18:31:21Z"
        }
        result = codemeta_date_created.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2015-11-09")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_flask_creation_date(self, mock_fetch):
        """Test creation date extraction from Flask."""
        mock_fetch.return_value = {
            "created_at": "2010-04-16T13:37:28Z"
        }
        result = codemeta_date_created.get("https://github.com/pallets/flask")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2010-04-16")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_rust_creation_date(self, mock_fetch):
        """Test creation date extraction from Rust."""
        mock_fetch.return_value = {
            "created_at": "2010-06-16T20:39:54Z"
        }
        result = codemeta_date_created.get("https://github.com/rust-lang/rust")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2010-06-16")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_dryad_creation_date(self, mock_fetch):
        """Test creation date extraction from Dryad."""
        mock_fetch.return_value = {
            "created_at": "2022-07-12T18:34:47Z"
        }
        result = codemeta_date_created.get("https://github.com/Dryad-lang/Dryad")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2022-07-12")


class TestDateParsing(unittest.TestCase):
    """Test date parsing and formatting."""

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_different_date_formats(self, mock_fetch):
        """Test parsing of different GitHub date formats."""
        test_cases = [
            ("2020-01-15T10:30:45Z", "2020-01-15"),
            ("2015-11-09T18:31:21Z", "2015-11-09"),
            ("2010-04-16T13:37:28Z", "2010-04-16"),
            ("2025-12-31T23:59:59Z", "2025-12-31"),
        ]
        
        for github_date, expected_iso in test_cases:
            mock_fetch.return_value = {"created_at": github_date}
            result = codemeta_date_created.get("https://github.com/owner/repo")
            self.assertEqual(result["dateCreated"], expected_iso)

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_leap_year_date(self, mock_fetch):
        """Test parsing of leap year date."""
        mock_fetch.return_value = {
            "created_at": "2020-02-29T12:00:00Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2020-02-29")

    @patch('src.modules.codemeta_date_created.fetch_repository_info')
    def test_year_boundary_date(self, mock_fetch):
        """Test parsing of year boundary date."""
        mock_fetch.return_value = {
            "created_at": "2020-12-31T23:59:59Z"
        }
        result = codemeta_date_created.get("https://github.com/owner/repo")
        
        self.assertIn("dateCreated", result)
        self.assertEqual(result["dateCreated"], "2020-12-31")


if __name__ == '__main__':
    unittest.main()
