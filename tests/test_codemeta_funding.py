#!/usr/bin/env python3
"""
Unit tests for the codemeta_funding module.

Tests cover:
- Funding extraction from various sources
- Duplicate removal
- Integration with the orchestrator
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_funding import (
    fetch_funding_yml,
    fetch_funding_from_readme,
    fetch_funding_from_file,
    fetch_funding_from_package_json,
    remove_duplicate_funding,
    get,
)


class TestFundingYmlExtraction(unittest.TestCase):
    """Test funding extraction from FUNDING.yml."""

    def test_fetch_funding_yml_returns_list(self):
        """Test that fetch_funding_yml returns a list."""
        result = fetch_funding_yml("tensorflow", "tensorflow")
        self.assertIsInstance(result, list)

    def test_fetch_funding_yml_with_invalid_repo(self):
        """Test fetch_funding_yml with nonexistent repository."""
        result = fetch_funding_yml("nonexistent-user-xyz", "nonexistent-repo-xyz")
        self.assertIsInstance(result, list)


class TestFundingReadmeExtraction(unittest.TestCase):
    """Test funding extraction from README."""

    def test_fetch_funding_from_readme_returns_list(self):
        """Test that fetch_funding_from_readme returns a list."""
        result = fetch_funding_from_readme("tensorflow", "tensorflow")
        self.assertIsInstance(result, list)

    def test_fetch_funding_from_readme_with_invalid_repo(self):
        """Test fetch_funding_from_readme with nonexistent repository."""
        result = fetch_funding_from_readme("nonexistent-user-xyz", "nonexistent-repo-xyz")
        self.assertIsInstance(result, list)


class TestDuplicateRemoval(unittest.TestCase):
    """Test duplicate removal functionality."""

    def test_remove_exact_duplicates(self):
        """Test removal of exact duplicate funding sources."""
        funding = [
            {"type": "Patreon", "url": "https://patreon.com/example"},
            {"type": "Patreon", "url": "https://patreon.com/example"},
            {"type": "Ko-fi", "url": "https://ko-fi.com/example"},
        ]

        result = remove_duplicate_funding(funding)
        self.assertEqual(len(result), 2)

    def test_remove_case_insensitive_duplicates(self):
        """Test removal of case-insensitive duplicates."""
        funding = [
            {"type": "Patreon", "url": "https://patreon.com/example"},
            {"type": "Patreon", "url": "https://patreon.com/EXAMPLE"},
        ]

        result = remove_duplicate_funding(funding)
        self.assertEqual(len(result), 1)

    def test_keep_different_funding_sources(self):
        """Test that different funding sources are kept."""
        funding = [
            {"type": "Patreon", "url": "https://patreon.com/example1"},
            {"type": "Ko-fi", "url": "https://ko-fi.com/example2"},
            {"type": "GitHub Sponsors", "url": "https://github.com/sponsors/example3"},
        ]

        result = remove_duplicate_funding(funding)
        self.assertEqual(len(result), 3)

    def test_remove_duplicates_empty_list(self):
        """Test duplicate removal with empty list."""
        result = remove_duplicate_funding([])
        self.assertEqual(result, [])


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    def test_get_returns_dict(self):
        """Test that get() returns a dictionary."""
        result = get("https://github.com/tensorflow/tensorflow")
        self.assertIsInstance(result, dict)

    def test_get_returns_funder_key(self):
        """Test that get() returns a 'funder' key when funding is found."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result:  # Only check if funding was found
            self.assertIn("funder", result)

    def test_get_returns_list_of_funders(self):
        """Test that get() returns a list for funder property."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "funder" in result:
            self.assertIsInstance(result["funder"], list)

    def test_get_with_invalid_url(self):
        """Test get() with invalid repository URL."""
        result = get("not-a-valid-url")
        self.assertEqual(result, {})

    def test_get_with_nonexistent_repository(self):
        """Test get() with nonexistent repository."""
        result = get("https://github.com/nonexistent-user-xyz/nonexistent-repo-xyz")
        # Should return empty dict or dict without funder
        self.assertIsInstance(result, dict)


class TestFunderContent(unittest.TestCase):
    """Test the content and quality of extracted funding information."""

    def test_funders_have_type(self):
        """Test that all funders have a type."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "funder" in result:
            for funder in result["funder"]:
                self.assertIn("type", funder)
                self.assertIsInstance(funder["type"], str)
                self.assertGreater(len(funder["type"]), 0)

    def test_funders_have_url(self):
        """Test that all funders have a URL."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "funder" in result:
            for funder in result["funder"]:
                self.assertIn("url", funder)
                self.assertIsInstance(funder["url"], str)
                self.assertTrue(funder["url"].startswith("http"))

    def test_funders_are_unique(self):
        """Test that there are no duplicate funders."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "funder" in result:
            funders = result["funder"]
            urls = [f.get("url", "") for f in funders]
            # Check that all URLs are unique
            self.assertEqual(len(urls), len(set(urls)))


class TestRealRepositories(unittest.TestCase):
    """Test funding extraction on real repositories."""

    def test_tensorflow_funding(self):
        """Test funding extraction from TensorFlow repository."""
        result = get("https://github.com/tensorflow/tensorflow")
        # TensorFlow may or may not have funding info
        self.assertIsInstance(result, dict)

    def test_rust_funding(self):
        """Test funding extraction from Rust repository."""
        result = get("https://github.com/rust-lang/rust")
        # Rust may or may not have funding info
        self.assertIsInstance(result, dict)

    def test_vue_funding(self):
        """Test funding extraction from Vue.js repository."""
        result = get("https://github.com/vuejs/vue")
        # Vue.js may or may not have funding info
        self.assertIsInstance(result, dict)


class TestFunderStructure(unittest.TestCase):
    """Test the structure of funder data."""

    def test_funder_has_required_fields(self):
        """Test that funders have required fields."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "funder" in result:
            for funder in result["funder"]:
                # Must have type and url
                self.assertIn("type", funder)
                self.assertIn("url", funder)

    def test_funder_url_is_valid(self):
        """Test that funder URLs are valid."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "funder" in result:
            for funder in result["funder"]:
                url = funder.get("url", "")
                # Should start with http
                self.assertTrue(url.startswith("http"))
                # Should not have spaces
                self.assertNotIn(" ", url)


if __name__ == "__main__":
    unittest.main()
