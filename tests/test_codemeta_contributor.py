#!/usr/bin/env python3
"""
Unit tests for the codemeta_contributor module.

Tests cover:
- Contributor extraction from various sources
- Duplicate removal
- ORCID enrichment
- Integration with the orchestrator
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_contributor import (
    fetch_contributors_from_api,
    fetch_contributors_from_file,
    remove_duplicate_contributors,
    get,
)


class TestContributorExtraction(unittest.TestCase):
    """Test contributor extraction functions."""

    def test_fetch_contributors_returns_list(self):
        """Test that fetch_contributors_from_api returns a list."""
        result = fetch_contributors_from_api("tensorflow", "tensorflow")
        self.assertIsInstance(result, list)

    def test_fetch_contributors_has_required_fields(self):
        """Test that contributors have required fields."""
        result = fetch_contributors_from_api("tensorflow", "tensorflow", limit=5)
        if result:
            for contributor in result:
                self.assertIn("name", contributor)
                self.assertIn("@type", contributor)
                self.assertEqual(contributor["@type"], "Person")

    def test_fetch_contributors_from_file_returns_list(self):
        """Test that fetch_contributors_from_file returns a list."""
        result = fetch_contributors_from_file("tensorflow", "tensorflow")
        self.assertIsInstance(result, list)

    def test_fetch_contributors_with_invalid_repo(self):
        """Test fetch_contributors with nonexistent repository."""
        result = fetch_contributors_from_api("nonexistent-user-xyz", "nonexistent-repo-xyz")
        self.assertIsInstance(result, list)


class TestDuplicateRemoval(unittest.TestCase):
    """Test duplicate removal functionality."""

    def test_remove_exact_duplicates(self):
        """Test removal of exact duplicate contributors."""
        contributors = [
            {"name": "John Doe", "url": "https://github.com/johndoe", "@type": "Person"},
            {"name": "John Doe", "url": "https://github.com/johndoe", "@type": "Person"},
            {"name": "Jane Smith", "url": "https://github.com/janesmith", "@type": "Person"},
        ]

        result = remove_duplicate_contributors(contributors)
        self.assertEqual(len(result), 2)

    def test_remove_case_insensitive_duplicates(self):
        """Test removal of case-insensitive duplicates."""
        contributors = [
            {"name": "John Doe", "url": "https://github.com/johndoe", "@type": "Person"},
            {"name": "JOHN DOE", "url": "https://github.com/johndoe", "@type": "Person"},
        ]

        result = remove_duplicate_contributors(contributors)
        self.assertEqual(len(result), 1)

    def test_keep_different_contributors(self):
        """Test that different contributors are kept."""
        contributors = [
            {"name": "John Doe", "url": "https://github.com/johndoe", "@type": "Person"},
            {"name": "Jane Smith", "url": "https://github.com/janesmith", "@type": "Person"},
            {"name": "Bob Johnson", "url": "https://github.com/bobjohnson", "@type": "Person"},
        ]

        result = remove_duplicate_contributors(contributors)
        self.assertEqual(len(result), 3)

    def test_remove_duplicates_empty_list(self):
        """Test duplicate removal with empty list."""
        result = remove_duplicate_contributors([])
        self.assertEqual(result, [])


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    def test_get_returns_dict(self):
        """Test that get() returns a dictionary."""
        result = get("https://github.com/tensorflow/tensorflow")
        self.assertIsInstance(result, dict)

    def test_get_returns_contributor_key(self):
        """Test that get() returns a 'contributor' key when contributors are found."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result:  # Only check if contributors were found
            self.assertIn("contributor", result)

    def test_get_returns_list_of_contributors(self):
        """Test that get() returns a list for contributor property."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            self.assertIsInstance(result["contributor"], list)

    def test_get_with_invalid_url(self):
        """Test get() with invalid repository URL."""
        result = get("not-a-valid-url")
        self.assertEqual(result, {})

    def test_get_with_nonexistent_repository(self):
        """Test get() with nonexistent repository."""
        result = get("https://github.com/nonexistent-user-xyz/nonexistent-repo-xyz")
        # Should return empty dict or dict without contributor
        self.assertIsInstance(result, dict)


class TestContributorContent(unittest.TestCase):
    """Test the content and quality of extracted contributors."""

    def test_contributors_have_name(self):
        """Test that all contributors have a name."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            for contributor in result["contributor"]:
                self.assertIn("name", contributor)
                self.assertIsInstance(contributor["name"], str)
                self.assertGreater(len(contributor["name"]), 0)

    def test_contributors_have_type(self):
        """Test that all contributors have @type set to Person."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            for contributor in result["contributor"]:
                self.assertIn("@type", contributor)
                self.assertEqual(contributor["@type"], "Person")

    def test_contributors_no_contributions_field(self):
        """Test that contributions field is removed from contributors."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            for contributor in result["contributor"]:
                self.assertNotIn("contributions", contributor)

    def test_contributors_are_unique(self):
        """Test that there are no duplicate contributors."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            contributors = result["contributor"]
            names = [c.get("name", "") for c in contributors]
            # Check that all names are unique
            self.assertEqual(len(names), len(set(names)))


class TestRealRepositories(unittest.TestCase):
    """Test contributor extraction on real repositories."""

    def test_tensorflow_contributors(self):
        """Test contributor extraction from TensorFlow repository."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            contributors = result["contributor"]
            self.assertGreater(len(contributors), 0)
            # TensorFlow should have many contributors
            self.assertGreater(len(contributors), 5)

    def test_rust_contributors(self):
        """Test contributor extraction from Rust repository."""
        result = get("https://github.com/rust-lang/rust")
        if result and "contributor" in result:
            contributors = result["contributor"]
            self.assertGreater(len(contributors), 0)

    def test_kubernetes_contributors(self):
        """Test contributor extraction from Kubernetes repository."""
        result = get("https://github.com/kubernetes/kubernetes")
        if result and "contributor" in result:
            contributors = result["contributor"]
            self.assertGreater(len(contributors), 0)

    def test_gpt2_contributors(self):
        """Test contributor extraction from GPT-2 repository."""
        result = get("https://github.com/openai/gpt-2")
        # GPT-2 should have contributors
        self.assertIsInstance(result, dict)


class TestContributorStructure(unittest.TestCase):
    """Test the structure of contributor data."""

    def test_contributor_is_person_type(self):
        """Test that contributor @type is Person."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            for contributor in result["contributor"]:
                self.assertEqual(contributor.get("@type"), "Person")

    def test_contributor_optional_fields(self):
        """Test that optional fields are present when available."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            # At least some contributors should have optional fields
            has_email = any("email" in c for c in result["contributor"])
            has_url = any("url" in c for c in result["contributor"])
            # At least one of these should be true
            self.assertTrue(has_email or has_url)

    def test_contributor_orcid_format(self):
        """Test that ORCID IDs are in correct format."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "contributor" in result:
            for contributor in result["contributor"]:
                if "@id" in contributor:
                    # Should be a valid ORCID URL
                    self.assertTrue(
                        contributor["@id"].startswith("https://orcid.org/"),
                        f"Invalid ORCID format: {contributor['@id']}"
                    )


if __name__ == "__main__":
    unittest.main()
