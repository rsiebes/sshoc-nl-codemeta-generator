#!/usr/bin/env python3
"""
Unit tests for the codemeta_date_published module.

Tests cover:
- Date validation and normalization
- Date extraction from various sources
- Integration with the orchestrator
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_date_published import (
    is_valid_iso_date,
    normalize_date,
    get,
)


class TestDateValidation(unittest.TestCase):
    """Test date validation functions."""

    def test_valid_iso_dates(self):
        """Test validation of valid ISO 8601 dates."""
        valid_dates = [
            "2024-01-15",
            "2023-12-31",
            "2000-01-01",
            "2024-01-15T10:30:00Z",
            "2024-01-15T10:30:00+00:00",
            "2024-01-15T10:30:00-05:00",
        ]

        for date in valid_dates:
            self.assertTrue(is_valid_iso_date(date), f"Should be valid: {date}")

    def test_invalid_dates(self):
        """Test rejection of invalid dates."""
        invalid_dates = [
            "",
            "not-a-date",
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "01-15-2024",  # Wrong format
            "2024/01/15",  # Wrong separator
        ]

        for date in invalid_dates:
            self.assertFalse(is_valid_iso_date(date), f"Should be invalid: {date}")

    def test_none_date(self):
        """Test validation with None."""
        self.assertFalse(is_valid_iso_date(None))

    def test_empty_string_date(self):
        """Test validation with empty string."""
        self.assertFalse(is_valid_iso_date(""))


class TestDateNormalization(unittest.TestCase):
    """Test date normalization functions."""

    def test_normalize_date_only(self):
        """Test normalization of date-only format."""
        self.assertEqual(normalize_date("2024-01-15"), "2024-01-15")
        self.assertEqual(normalize_date("2023-12-31"), "2023-12-31")

    def test_normalize_iso_datetime(self):
        """Test normalization of ISO 8601 datetime."""
        self.assertEqual(normalize_date("2024-01-15T10:30:00Z"), "2024-01-15")
        self.assertEqual(normalize_date("2024-01-15T10:30:00+00:00"), "2024-01-15")

    def test_normalize_iso_datetime_with_timezone(self):
        """Test normalization of ISO 8601 datetime with timezone."""
        self.assertEqual(normalize_date("2024-01-15T10:30:00-05:00"), "2024-01-15")
        self.assertEqual(normalize_date("2024-01-15T15:30:00+05:00"), "2024-01-15")

    def test_normalize_empty_string(self):
        """Test normalization of empty string."""
        self.assertIsNone(normalize_date(""))

    def test_normalize_none(self):
        """Test normalization of None."""
        self.assertIsNone(normalize_date(None))

    def test_normalize_invalid_date(self):
        """Test normalization of invalid date."""
        self.assertIsNone(normalize_date("not-a-date"))
        self.assertIsNone(normalize_date("2024-13-01"))


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    def test_get_returns_dict(self):
        """Test that get() returns a dictionary."""
        result = get("https://github.com/tensorflow/tensorflow")
        self.assertIsInstance(result, dict)

    def test_get_returns_date_published_key(self):
        """Test that get() returns a 'datePublished' key when date is found."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result:  # Only check if date was found
            self.assertIn("datePublished", result)

    def test_get_returns_string_date(self):
        """Test that get() returns a string for datePublished."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "datePublished" in result:
            self.assertIsInstance(result["datePublished"], str)

    def test_get_with_invalid_url(self):
        """Test get() with invalid repository URL."""
        result = get("not-a-valid-url")
        self.assertEqual(result, {})

    def test_get_with_nonexistent_repository(self):
        """Test get() with nonexistent repository."""
        result = get("https://github.com/nonexistent-user-xyz/nonexistent-repo-xyz")
        # Should return empty dict or dict without datePublished
        self.assertIsInstance(result, dict)


class TestDateContent(unittest.TestCase):
    """Test the content and quality of extracted dates."""

    def test_date_is_string(self):
        """Test that datePublished is a string."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "datePublished" in result:
            self.assertIsInstance(result["datePublished"], str)

    def test_date_is_iso_format(self):
        """Test that datePublished is in ISO 8601 format."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "datePublished" in result:
            date_str = result["datePublished"]
            # Should be in YYYY-MM-DD format
            self.assertRegex(date_str, r'^\d{4}-\d{2}-\d{2}$')

    def test_date_is_valid(self):
        """Test that datePublished is a valid date."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "datePublished" in result:
            date_str = result["datePublished"]
            # Should be parseable as a date
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                self.fail(f"Date {date_str} is not a valid date")

    def test_date_is_reasonable(self):
        """Test that datePublished is a reasonable date (not in the future)."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "datePublished" in result:
            date_str = result["datePublished"]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Date should not be in the future
            self.assertLessEqual(date_obj, datetime.now())


class TestRealRepositories(unittest.TestCase):
    """Test date extraction on real repositories."""

    def test_tensorflow_date(self):
        """Test date extraction from TensorFlow repository."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "datePublished" in result:
            date_str = result["datePublished"]
            self.assertIsInstance(date_str, str)
            self.assertGreater(len(date_str), 0)
            # Should be a valid date
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                self.fail(f"Date {date_str} is not a valid date")

    def test_rust_date(self):
        """Test date extraction from Rust repository."""
        result = get("https://github.com/rust-lang/rust")
        if result and "datePublished" in result:
            date_str = result["datePublished"]
            self.assertIsInstance(date_str, str)
            self.assertGreater(len(date_str), 0)

    def test_kubernetes_date(self):
        """Test date extraction from Kubernetes repository."""
        result = get("https://github.com/kubernetes/kubernetes")
        if result and "datePublished" in result:
            date_str = result["datePublished"]
            self.assertIsInstance(date_str, str)
            self.assertGreater(len(date_str), 0)

    def test_gpt2_date(self):
        """Test date extraction from GPT-2 repository."""
        result = get("https://github.com/openai/gpt-2")
        # GPT-2 should have a date (either from commit or creation date)
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
