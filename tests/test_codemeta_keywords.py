#!/usr/bin/env python3
"""
Unit tests for the codemeta_keywords module.

Tests cover:
- Keyword extraction from various sources
- Deduplication and normalization
- Integration with the orchestrator
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_keywords import (
    extract_keywords_from_description,
    extract_keywords_from_topics,
    deduplicate_and_normalize_keywords,
    get,
)


class TestKeywordExtraction(unittest.TestCase):
    """Test keyword extraction functions."""

    def test_extract_keywords_from_description_with_programming_keywords(self):
        """Test extraction of programming keywords from description."""
        description = "A machine learning framework for deep learning and neural networks"
        keywords = extract_keywords_from_description(description)

        self.assertIn("machine learning", keywords)
        self.assertIn("deep learning", keywords)
        self.assertIn("neural network", keywords)

    def test_extract_keywords_from_description_with_domain_keywords(self):
        """Test extraction of domain-specific keywords from description."""
        description = "Natural language processing toolkit for NLP and text processing"
        keywords = extract_keywords_from_description(description)

        self.assertIn("natural language", keywords)
        self.assertIn("text processing", keywords)

    def test_extract_keywords_from_description_empty(self):
        """Test extraction from empty description."""
        keywords = extract_keywords_from_description("")
        self.assertEqual(len(keywords), 0)

    def test_extract_keywords_from_description_none(self):
        """Test extraction from None description."""
        keywords = extract_keywords_from_description(None)
        self.assertEqual(len(keywords), 0)

    def test_extract_keywords_from_description_case_insensitive(self):
        """Test that keyword extraction is case-insensitive."""
        description = "MACHINE LEARNING and Deep Learning"
        keywords = extract_keywords_from_description(description)

        self.assertIn("machine learning", keywords)
        self.assertIn("deep learning", keywords)

    def test_extract_keywords_from_description_no_matches(self):
        """Test extraction when no known keywords are found."""
        description = "A simple tool for doing stuff"
        keywords = extract_keywords_from_description(description)

        # Should not contain any of our known keywords
        self.assertEqual(len(keywords), 0)


class TestDeduplicationAndNormalization(unittest.TestCase):
    """Test deduplication and normalization of keywords."""

    def test_deduplicate_keywords(self):
        """Test deduplication of keywords."""
        keywords = {"python", "python", "javascript", "python"}
        result = deduplicate_and_normalize_keywords(keywords)

        self.assertEqual(len(result), 2)
        self.assertIn("python", result)
        self.assertIn("javascript", result)

    def test_normalize_keywords_sorting(self):
        """Test that keywords are sorted alphabetically."""
        keywords = {"zebra", "apple", "banana"}
        result = deduplicate_and_normalize_keywords(keywords)

        self.assertEqual(result, ["apple", "banana", "zebra"])

    def test_filter_short_keywords(self):
        """Test that very short keywords are filtered out."""
        keywords = {"a", "ab", "abc", "abcd"}
        result = deduplicate_and_normalize_keywords(keywords)

        # Only keywords with 3+ characters should remain
        self.assertNotIn("a", result)
        self.assertNotIn("ab", result)
        self.assertIn("abc", result)
        self.assertIn("abcd", result)

    def test_filter_empty_strings(self):
        """Test that empty strings are filtered out."""
        keywords = {"", "python", "   ", "javascript"}
        result = deduplicate_and_normalize_keywords(keywords)

        self.assertNotIn("", result)
        self.assertIn("python", result)
        self.assertIn("javascript", result)

    def test_normalize_whitespace(self):
        """Test that whitespace is normalized."""
        keywords = {"  python  ", "javascript", "  golang  "}
        result = deduplicate_and_normalize_keywords(keywords)

        self.assertIn("python", result)
        self.assertIn("javascript", result)
        self.assertIn("golang", result)


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    def test_get_returns_dict(self):
        """Test that get() returns a dictionary."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        self.assertIsInstance(result, dict)

    def test_get_returns_keywords_key(self):
        """Test that get() returns a 'keywords' key when keywords are found."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result:  # Only check if keywords were found
            self.assertIn("keywords", result)

    def test_get_returns_list_of_strings(self):
        """Test that get() returns a list of strings for keywords."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "keywords" in result:
            self.assertIsInstance(result["keywords"], list)
            for keyword in result["keywords"]:
                self.assertIsInstance(keyword, str)

    def test_get_with_invalid_url(self):
        """Test get() with invalid repository URL."""
        result = get("not-a-valid-url")
        self.assertEqual(result, {})

    def test_get_with_nonexistent_repository(self):
        """Test get() with nonexistent repository."""
        result = get("https://github.com/nonexistent-user-xyz/nonexistent-repo-xyz")
        # Should return empty dict or dict without keywords
        self.assertIsInstance(result, dict)


class TestKeywordContent(unittest.TestCase):
    """Test the content and quality of extracted keywords."""

    def test_keywords_are_lowercase(self):
        """Test that all keywords are lowercase."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "keywords" in result:
            for keyword in result["keywords"]:
                self.assertEqual(keyword, keyword.lower())

    def test_keywords_no_leading_trailing_whitespace(self):
        """Test that keywords have no leading/trailing whitespace."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "keywords" in result:
            for keyword in result["keywords"]:
                self.assertEqual(keyword, keyword.strip())

    def test_keywords_minimum_length(self):
        """Test that all keywords have minimum length of 3 characters."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "keywords" in result:
            for keyword in result["keywords"]:
                self.assertGreaterEqual(len(keyword), 3)


class TestRealRepositories(unittest.TestCase):
    """Test keyword extraction on real repositories."""

    def test_tensorflow_keywords(self):
        """Test keyword extraction from TensorFlow repository."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "keywords" in result:
            keywords = result["keywords"]
            # TensorFlow should have machine learning related keywords
            self.assertGreater(len(keywords), 0)
            # Check for expected keywords (case-insensitive)
            keywords_lower = [k.lower() for k in keywords]
            # At least one of these should be present
            expected = ["tensorflow", "machine learning", "deep learning", "neural network", "python"]
            self.assertTrue(any(exp in keywords_lower for exp in expected))

    def test_gpt2_keywords(self):
        """Test keyword extraction from GPT-2 repository."""
        result = get("https://github.com/openai/gpt-2")
        if result and "keywords" in result:
            keywords = result["keywords"]
            self.assertGreater(len(keywords), 0)

    def test_keywords_are_unique(self):
        """Test that extracted keywords are unique (no duplicates)."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "keywords" in result:
            keywords = result["keywords"]
            # Check that all keywords are unique
            self.assertEqual(len(keywords), len(set(keywords)))


if __name__ == "__main__":
    unittest.main()
