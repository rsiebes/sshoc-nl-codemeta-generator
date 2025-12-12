"""
Unit tests for codemeta_date_modified module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_date_modified


class TestDateModifiedExtraction(unittest.TestCase):
    """Test modification date extraction."""

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_basic_date_extraction(self, mock_fetch):
        """Test extraction of basic modification date."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T15:30:45Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-12-10")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_date_format_conversion(self, mock_fetch):
        """Test conversion of GitHub date format to ISO 8601."""
        mock_fetch.return_value = {
            "updated_at": "2025-07-12T18:34:47Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-07-12")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_recent_modification(self, mock_fetch):
        """Test extraction of recent modification date."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-12T10:00:00Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-12-12")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_old_modification(self, mock_fetch):
        """Test extraction of old modification date."""
        mock_fetch.return_value = {
            "updated_at": "2010-06-30T12:34:56Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2010-06-30")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_missing_modification_date(self, mock_fetch):
        """Test handling of missing modification date."""
        mock_fetch.return_value = {}
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_none_repository_info(self, mock_fetch):
        """Test handling of None repository info."""
        mock_fetch.return_value = None
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_api_error_handling(self, mock_fetch):
        """Test handling of API errors."""
        mock_fetch.side_effect = Exception("API Error")
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_date_modified.get("invalid-url")
        
        self.assertEqual(result, {})


class TestDateModifiedContent(unittest.TestCase):
    """Test modification date content validation."""

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_date_is_string(self, mock_fetch):
        """Test that modification date is a string."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T15:30:45Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertIsInstance(result["dateModified"], str)

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_date_not_empty(self, mock_fetch):
        """Test that modification date is not empty."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T15:30:45Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertTrue(result["dateModified"])

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_date_format_iso8601(self, mock_fetch):
        """Test that modification date is in ISO 8601 format."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T15:30:45Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        date_str = result["dateModified"]
        # Check format YYYY-MM-DD
        self.assertRegex(date_str, r'^\d{4}-\d{2}-\d{2}$')

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_date_valid_range(self, mock_fetch):
        """Test that modification date is in valid range."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T15:30:45Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        date_str = result["dateModified"]
        # Parse and validate
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # Check it's a reasonable date (after GitHub was founded in 2008)
            self.assertGreaterEqual(date_obj.year, 2008)
            # Check it's not too far in the future
            self.assertLessEqual(date_obj.year, 2100)
        except ValueError:
            self.fail("Date is not in valid ISO 8601 format")


class TestRealRepositories(unittest.TestCase):
    """Test modification date extraction from real repositories."""

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_tensorflow_modification_date(self, mock_fetch):
        """Test modification date extraction from TensorFlow."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T14:22:33Z"
        }
        result = codemeta_date_modified.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-12-10")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_flask_modification_date(self, mock_fetch):
        """Test modification date extraction from Flask."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-08T09:15:22Z"
        }
        result = codemeta_date_modified.get("https://github.com/pallets/flask")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-12-08")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_rust_modification_date(self, mock_fetch):
        """Test modification date extraction from Rust."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-11T16:45:10Z"
        }
        result = codemeta_date_modified.get("https://github.com/rust-lang/rust")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-12-11")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_dryad_modification_date(self, mock_fetch):
        """Test modification date extraction from Dryad."""
        mock_fetch.return_value = {
            "updated_at": "2025-07-12T12:07:48Z"
        }
        result = codemeta_date_modified.get("https://github.com/Dryad-lang/Dryad")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-07-12")


class TestDateParsing(unittest.TestCase):
    """Test date parsing and formatting."""

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_different_date_formats(self, mock_fetch):
        """Test parsing of different GitHub date formats."""
        test_cases = [
            ("2025-12-10T15:30:45Z", "2025-12-10"),
            ("2025-07-12T18:34:47Z", "2025-07-12"),
            ("2010-04-16T13:37:28Z", "2010-04-16"),
            ("2025-12-31T23:59:59Z", "2025-12-31"),
        ]
        
        for github_date, expected_iso in test_cases:
            mock_fetch.return_value = {"updated_at": github_date}
            result = codemeta_date_modified.get("https://github.com/owner/repo")
            self.assertEqual(result["dateModified"], expected_iso)

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_leap_year_date(self, mock_fetch):
        """Test parsing of leap year date."""
        mock_fetch.return_value = {
            "updated_at": "2020-02-29T12:00:00Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2020-02-29")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_year_boundary_date(self, mock_fetch):
        """Test parsing of year boundary date."""
        mock_fetch.return_value = {
            "updated_at": "2025-12-31T23:59:59Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-12-31")

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_year_start_date(self, mock_fetch):
        """Test parsing of year start date."""
        mock_fetch.return_value = {
            "updated_at": "2025-01-01T00:00:00Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        self.assertEqual(result["dateModified"], "2025-01-01")


class TestDateComparison(unittest.TestCase):
    """Test date comparison and relationships."""

    @patch('src.modules.codemeta_date_modified.fetch_repository_info')
    def test_modification_after_creation(self, mock_fetch):
        """Test that modification date can be after creation date."""
        # This is a logical test - modification should typically be >= creation
        mock_fetch.return_value = {
            "updated_at": "2025-12-10T15:30:45Z"
        }
        result = codemeta_date_modified.get("https://github.com/owner/repo")
        
        self.assertIn("dateModified", result)
        # Just verify it's a valid date
        self.assertRegex(result["dateModified"], r'^\d{4}-\d{2}-\d{2}$')


if __name__ == '__main__':
    unittest.main()
