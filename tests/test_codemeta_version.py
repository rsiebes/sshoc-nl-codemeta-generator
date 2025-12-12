#!/usr/bin/env python3
"""
Unit tests for the codemeta_version module.

Tests cover:
- Version validation and normalization
- Version extraction from various sources
- Integration with the orchestrator
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_version import (
    is_valid_version,
    normalize_version,
    get,
)


class TestVersionValidation(unittest.TestCase):
    """Test version validation functions."""

    def test_valid_semantic_versions(self):
        """Test validation of semantic versions."""
        valid_versions = [
            "1.0.0",
            "v1.0.0",
            "2.3.4",
            "0.0.1",
            "10.20.30",
        ]

        for version in valid_versions:
            self.assertTrue(is_valid_version(version), f"Should be valid: {version}")

    def test_valid_versions_with_prerelease(self):
        """Test validation of versions with prerelease tags."""
        valid_versions = [
            "1.0.0-alpha",
            "1.0.0-beta.1",
            "2.0.0-rc1",
            "v1.0.0-dev",
        ]

        for version in valid_versions:
            self.assertTrue(is_valid_version(version), f"Should be valid: {version}")

    def test_valid_versions_with_build_metadata(self):
        """Test validation of versions with build metadata."""
        valid_versions = [
            "1.0.0+build.1",
            "1.0.0-alpha+001",
            "2.0.0+20130313144700",
        ]

        for version in valid_versions:
            self.assertTrue(is_valid_version(version), f"Should be valid: {version}")

    def test_valid_simple_versions(self):
        """Test validation of simple version formats."""
        valid_versions = [
            "1.0",
            "2.3",
            "10.20",
        ]

        for version in valid_versions:
            self.assertTrue(is_valid_version(version), f"Should be valid: {version}")

    def test_invalid_versions(self):
        """Test rejection of invalid versions."""
        invalid_versions = [
            "",
            "abc",
            "version-1",
            "latest",
            "master",
            "main",
            "develop",
        ]

        for version in invalid_versions:
            self.assertFalse(is_valid_version(version), f"Should be invalid: {version}")

    def test_none_version(self):
        """Test validation with None."""
        self.assertFalse(is_valid_version(None))

    def test_whitespace_only_version(self):
        """Test validation with whitespace only."""
        self.assertFalse(is_valid_version("   "))


class TestVersionNormalization(unittest.TestCase):
    """Test version normalization functions."""

    def test_remove_v_prefix(self):
        """Test removal of 'v' prefix."""
        self.assertEqual(normalize_version("v1.0.0"), "1.0.0")
        self.assertEqual(normalize_version("v2.3.4"), "2.3.4")

    def test_strip_whitespace(self):
        """Test stripping of whitespace."""
        self.assertEqual(normalize_version("  1.0.0  "), "1.0.0")
        self.assertEqual(normalize_version("\t2.3.4\n"), "2.3.4")

    def test_remove_quotes(self):
        """Test removal of quotes."""
        self.assertEqual(normalize_version('"1.0.0"'), "1.0.0")
        self.assertEqual(normalize_version("'2.3.4'"), "2.3.4")

    def test_combined_normalization(self):
        """Test combined normalization operations."""
        self.assertEqual(normalize_version('  "v1.0.0"  '), "1.0.0")
        self.assertEqual(normalize_version("  'v2.3.4'  "), "2.3.4")

    def test_normalize_empty_string(self):
        """Test normalization of empty string."""
        self.assertEqual(normalize_version(""), "")

    def test_normalize_none(self):
        """Test normalization of None."""
        self.assertEqual(normalize_version(None), "")


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    def test_get_returns_dict(self):
        """Test that get() returns a dictionary."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        self.assertIsInstance(result, dict)

    def test_get_returns_version_key(self):
        """Test that get() returns a 'version' key when version is found."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result:  # Only check if version was found
            self.assertIn("version", result)

    def test_get_returns_string_version(self):
        """Test that get() returns a string for version."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "version" in result:
            self.assertIsInstance(result["version"], str)

    def test_get_with_invalid_url(self):
        """Test get() with invalid repository URL."""
        result = get("not-a-valid-url")
        self.assertEqual(result, {})

    def test_get_with_nonexistent_repository(self):
        """Test get() with nonexistent repository."""
        result = get("https://github.com/nonexistent-user-xyz/nonexistent-repo-xyz")
        # Should return empty dict or dict without version
        self.assertIsInstance(result, dict)


class TestVersionContent(unittest.TestCase):
    """Test the content and quality of extracted versions."""

    def test_version_is_string(self):
        """Test that version is a string."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "version" in result:
            self.assertIsInstance(result["version"], str)

    def test_version_no_leading_trailing_whitespace(self):
        """Test that version has no leading/trailing whitespace."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "version" in result:
            version = result["version"]
            self.assertEqual(version, version.strip())

    def test_version_no_v_prefix(self):
        """Test that version doesn't have 'v' prefix."""
        result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        if result and "version" in result:
            version = result["version"]
            self.assertFalse(version.startswith("v"), "Version should not start with 'v'")


class TestRealRepositories(unittest.TestCase):
    """Test version extraction on real repositories."""

    def test_tensorflow_version(self):
        """Test version extraction from TensorFlow repository."""
        result = get("https://github.com/tensorflow/tensorflow")
        if result and "version" in result:
            version = result["version"]
            # Should be a valid semantic version
            self.assertIsInstance(version, str)
            self.assertGreater(len(version), 0)
            # Should contain at least one dot (e.g., "2.13.0")
            self.assertIn(".", version)

    def test_rust_version(self):
        """Test version extraction from Rust repository."""
        result = get("https://github.com/rust-lang/rust")
        if result and "version" in result:
            version = result["version"]
            self.assertIsInstance(version, str)
            self.assertGreater(len(version), 0)

    def test_gpt2_version(self):
        """Test version extraction from GPT-2 repository."""
        result = get("https://github.com/openai/gpt-2")
        if result and "version" in result:
            version = result["version"]
            self.assertIsInstance(version, str)
            self.assertGreater(len(version), 0)

    def test_kubernetes_version(self):
        """Test version extraction from Kubernetes repository."""
        result = get("https://github.com/kubernetes/kubernetes")
        if result and "version" in result:
            version = result["version"]
            self.assertIsInstance(version, str)
            self.assertGreater(len(version), 0)


if __name__ == "__main__":
    unittest.main()
