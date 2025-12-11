#!/usr/bin/env python3
"""
Unit tests for the codemeta_author module.

This module contains tests for:
- Author extraction from various sources
- ORCID identifier lookup
- Author data structure validation
- Integration with the orchestrator
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_author import (
    extract_authors_from_github_api,
    extract_authors_from_setup_py,
    extract_authors_from_pyproject_toml,
    extract_authors_from_package_json,
    find_orcid_for_author,
    get,
)


class TestAuthorExtraction:
    """Tests for author extraction from various sources."""

    @patch('src.modules.codemeta_author.requests.get')
    def test_extract_authors_from_github_api_valid(self, mock_get):
        """Test extracting authors from GitHub API."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "login": "testuser",
                "html_url": "https://github.com/testuser",
                "url": "https://api.github.com/users/testuser",
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock the user info request
        mock_user_response = MagicMock()
        mock_user_response.json.return_value = {
            "name": "Test User",
            "email": "test@example.com",
            "company": "Test Company",
        }
        mock_user_response.raise_for_status = MagicMock()

        mock_get.side_effect = [mock_response, mock_user_response]

        authors = extract_authors_from_github_api("owner", "repo")
        assert authors is not None, "Should extract authors"
        assert len(authors) > 0, "Should have at least one author"
        assert authors[0]["@type"] == "Person", "Should have Person type"
        print("✓ test_extract_authors_from_github_api_valid passed")

    @patch('src.modules.codemeta_author.fetch_file_content')
    def test_extract_authors_from_setup_py_valid(self, mock_fetch):
        """Test extracting authors from setup.py."""
        mock_fetch.return_value = 'author="John Doe", author_email="john@example.com"'

        authors = extract_authors_from_setup_py("owner", "repo")
        assert authors is not None, "Should extract authors"
        assert len(authors) > 0, "Should have at least one author"
        assert authors[0]["name"] == "John Doe", "Should have correct name"
        print("✓ test_extract_authors_from_setup_py_valid passed")

    @patch('src.modules.codemeta_author.fetch_file_content')
    def test_extract_authors_from_setup_py_not_found(self, mock_fetch):
        """Test extracting authors from non-existent setup.py."""
        mock_fetch.return_value = None

        authors = extract_authors_from_setup_py("owner", "repo")
        assert authors is None, "Should return None when file not found"
        print("✓ test_extract_authors_from_setup_py_not_found passed")

    @patch('src.modules.codemeta_author.fetch_file_content')
    def test_extract_authors_from_pyproject_toml_valid(self, mock_fetch):
        """Test extracting authors from pyproject.toml."""
        mock_fetch.return_value = '''
[project]
authors = [
    {name = "Jane Doe", email = "jane@example.com"},
    {name = "John Smith", email = "john@example.com"}
]
'''

        authors = extract_authors_from_pyproject_toml("owner", "repo")
        assert authors is not None, "Should extract authors"
        assert len(authors) >= 1, "Should have at least one author"
        print("✓ test_extract_authors_from_pyproject_toml_valid passed")

    @patch('src.modules.codemeta_author.fetch_file_content')
    def test_extract_authors_from_package_json_valid(self, mock_fetch):
        """Test extracting authors from package.json."""
        package_json = {
            "author": {
                "name": "Alice Developer",
                "email": "alice@example.com",
                "url": "https://example.com"
            }
        }
        mock_fetch.return_value = json.dumps(package_json)

        authors = extract_authors_from_package_json("owner", "repo")
        assert authors is not None, "Should extract authors"
        assert len(authors) > 0, "Should have at least one author"
        assert authors[0]["name"] == "Alice Developer", "Should have correct name"
        print("✓ test_extract_authors_from_package_json_valid passed")

    @patch('src.modules.codemeta_author.fetch_file_content')
    def test_extract_authors_from_package_json_string_format(self, mock_fetch):
        """Test extracting authors from package.json with string format."""
        package_json = {
            "author": "Bob Developer <bob@example.com>"
        }
        mock_fetch.return_value = json.dumps(package_json)

        authors = extract_authors_from_package_json("owner", "repo")
        assert authors is not None, "Should extract authors"
        assert len(authors) > 0, "Should have at least one author"
        assert authors[0]["name"] == "Bob Developer", "Should parse name correctly"
        assert authors[0]["email"] == "bob@example.com", "Should parse email correctly"
        print("✓ test_extract_authors_from_package_json_string_format passed")


class TestOrcidLookup:
    """Tests for ORCID identifier lookup."""

    @patch('src.modules.codemeta_author.requests.get')
    def test_find_orcid_for_author_found(self, mock_get):
        """Test finding ORCID for an author."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "orcid-identifier": {
                        "path": "0000-0001-2345-6789"
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        orcid = find_orcid_for_author("John Doe", "john@example.com")
        assert orcid is not None, "Should find ORCID"
        assert orcid == "0000-0001-2345-6789", "Should return correct ORCID"
        print("✓ test_find_orcid_for_author_found passed")

    @patch('src.modules.codemeta_author.requests.get')
    def test_find_orcid_for_author_not_found(self, mock_get):
        """Test when ORCID is not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        orcid = find_orcid_for_author("Unknown Author")
        assert orcid is None, "Should return None when ORCID not found"
        print("✓ test_find_orcid_for_author_not_found passed")

    def test_find_orcid_for_author_empty_name(self):
        """Test ORCID lookup with empty name."""
        orcid = find_orcid_for_author("")
        assert orcid is None, "Should return None for empty name"
        print("✓ test_find_orcid_for_author_empty_name passed")


class TestAuthorDataStructure:
    """Tests for author data structure validation."""

    @patch('src.modules.codemeta_author.requests.get')
    def test_author_has_required_fields(self, mock_get):
        """Test that extracted authors have required fields."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "login": "testuser",
                "html_url": "https://github.com/testuser",
                "url": "https://api.github.com/users/testuser",
            }
        ]
        mock_response.raise_for_status = MagicMock()

        mock_user_response = MagicMock()
        mock_user_response.json.return_value = {
            "name": "Test User",
            "email": "test@example.com",
        }
        mock_user_response.raise_for_status = MagicMock()

        mock_get.side_effect = [mock_response, mock_user_response]

        authors = extract_authors_from_github_api("owner", "repo")
        assert authors is not None, "Should extract authors"

        for author in authors:
            assert "@type" in author, "Author should have @type"
            assert author["@type"] == "Person", "Author type should be Person"
            assert "name" in author, "Author should have name"
        print("✓ test_author_has_required_fields passed")

    @patch('src.modules.codemeta_author.fetch_file_content')
    def test_author_with_orcid_has_id_field(self, mock_fetch):
        """Test that authors with ORCID have @id field."""
        mock_fetch.return_value = 'author="John Doe"'

        with patch('src.modules.codemeta_author.find_orcid_for_author') as mock_orcid:
            mock_orcid.return_value = "0000-0001-2345-6789"

            authors = extract_authors_from_setup_py("owner", "repo")
            assert authors is not None, "Should extract authors"

            for author in authors:
                if author.get("name") == "John Doe":
                    assert "@id" in author, "Author with ORCID should have @id"
                    assert "orcid.org" in author["@id"], "@id should be ORCID URL"
        print("✓ test_author_with_orcid_has_id_field passed")


class TestGetFunction:
    """Tests for the main get() function."""

    @patch('src.modules.codemeta_author.extract_authors_from_github_api')
    def test_get_returns_dict(self, mock_extract):
        """Test that get() returns a dictionary."""
        mock_extract.return_value = [
            {"name": "Test User", "@type": "Person"}
        ]

        result = get("https://github.com/owner/repo")
        assert isinstance(result, dict), "get() should return a dictionary"
        print("✓ test_get_returns_dict passed")

    @patch('src.modules.codemeta_author.extract_authors_from_github_api')
    def test_get_with_authors_found(self, mock_extract):
        """Test get() when authors are found."""
        mock_extract.return_value = [
            {"name": "Test User", "@type": "Person"}
        ]

        result = get("https://github.com/owner/repo")
        assert "author" in result, "Result should contain 'author' key"
        assert isinstance(result["author"], list), "Author should be a list"
        print("✓ test_get_with_authors_found passed")

    @patch('src.modules.codemeta_author.extract_authors_from_github_api')
    def test_get_with_no_authors_found(self, mock_extract):
        """Test get() when no authors are found."""
        mock_extract.return_value = None

        with patch('src.modules.codemeta_author.extract_authors_from_setup_py') as mock_setup:
            mock_setup.return_value = None

            with patch('src.modules.codemeta_author.extract_authors_from_pyproject_toml') as mock_toml:
                mock_toml.return_value = None

                with patch('src.modules.codemeta_author.extract_authors_from_package_json') as mock_pkg:
                    mock_pkg.return_value = None

                    result = get("https://github.com/owner/repo")
                    assert result == {}, "Should return empty dict when no authors found"
        print("✓ test_get_with_no_authors_found passed")

    def test_get_with_invalid_url(self):
        """Test get() with invalid URL."""
        result = get("invalid-url")
        assert result == {}, "Should return empty dict for invalid URL"
        print("✓ test_get_with_invalid_url passed")


def run_all_tests():
    """Run all author module tests."""
    print("=" * 80)
    print("RUNNING CODEMETA_AUTHOR MODULE TESTS")
    print("=" * 80)
    print()

    test_classes = [
        TestAuthorExtraction,
        TestOrcidLookup,
        TestAuthorDataStructure,
        TestGetFunction,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]

        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(test_instance, test_method)()
                passed_tests += 1
            except AssertionError as e:
                failed_tests += 1
                print(f"✗ {test_method} failed: {str(e)}")
            except Exception as e:
                failed_tests += 1
                print(f"✗ {test_method} failed with exception: {str(e)}")

    print()
    print("=" * 80)
    print(f"RESULTS: {passed_tests} passed, {failed_tests} failed out of {total_tests} tests")
    print("=" * 80)

    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
