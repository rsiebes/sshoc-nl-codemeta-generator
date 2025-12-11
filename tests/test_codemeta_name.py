#!/usr/bin/env python3
"""
Unit tests for the codemeta_name module.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_name import (
    extract_name_from_url,
    extract_name_from_setup_py,
    extract_name_from_pyproject_toml,
    extract_name_from_package_json,
    extract_name_from_readme,
    extract_name_from_repository_info,
    get
)


class TestNameExtraction:
    """Test suite for name extraction functions."""

    def test_extract_name_from_url_valid(self):
        """Test extracting name from a valid GitHub URL."""
        url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator"
        name = extract_name_from_url(url)
        assert name == "sshoc-nl-codemeta-generator", f"Expected 'sshoc-nl-codemeta-generator', got '{name}'"
        print("✓ test_extract_name_from_url_valid passed")

    def test_extract_name_from_url_with_git_suffix(self):
        """Test extracting name from a GitHub URL with .git suffix."""
        url = "https://github.com/rsiebes/sshoc-nl-codemeta-generator.git"
        name = extract_name_from_url(url)
        assert name == "sshoc-nl-codemeta-generator", f"Expected 'sshoc-nl-codemeta-generator', got '{name}'"
        print("✓ test_extract_name_from_url_with_git_suffix passed")

    def test_extract_name_from_url_invalid(self):
        """Test extracting name from an invalid URL."""
        url = "https://example.com/not-a-github-url"
        name = extract_name_from_url(url)
        assert name is None, f"Expected None, got '{name}'"
        print("✓ test_extract_name_from_url_invalid passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_setup_py_valid(self, mock_fetch):
        """Test extracting name from setup.py."""
        mock_fetch.return_value = 'setup(name="my-package", version="1.0.0")'
        name = extract_name_from_setup_py("owner", "repo")
        assert name == "my-package", f"Expected 'my-package', got '{name}'"
        print("✓ test_extract_name_from_setup_py_valid passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_setup_py_single_quotes(self, mock_fetch):
        """Test extracting name from setup.py with single quotes."""
        mock_fetch.return_value = "setup(name='my-package', version='1.0.0')"
        name = extract_name_from_setup_py("owner", "repo")
        assert name == "my-package", f"Expected 'my-package', got '{name}'"
        print("✓ test_extract_name_from_setup_py_single_quotes passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_setup_py_not_found(self, mock_fetch):
        """Test when setup.py doesn't exist."""
        mock_fetch.return_value = None
        name = extract_name_from_setup_py("owner", "repo")
        assert name is None, f"Expected None, got '{name}'"
        print("✓ test_extract_name_from_setup_py_not_found passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_pyproject_toml_valid(self, mock_fetch):
        """Test extracting name from pyproject.toml."""
        mock_fetch.return_value = '[project]\nname = "my-package"\nversion = "1.0.0"'
        name = extract_name_from_pyproject_toml("owner", "repo")
        assert name == "my-package", f"Expected 'my-package', got '{name}'"
        print("✓ test_extract_name_from_pyproject_toml_valid passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_pyproject_toml_single_quotes(self, mock_fetch):
        """Test extracting name from pyproject.toml with single quotes."""
        mock_fetch.return_value = "[project]\nname = 'my-package'\nversion = '1.0.0'"
        name = extract_name_from_pyproject_toml("owner", "repo")
        assert name == "my-package", f"Expected 'my-package', got '{name}'"
        print("✓ test_extract_name_from_pyproject_toml_single_quotes passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_package_json_valid(self, mock_fetch):
        """Test extracting name from package.json."""
        mock_fetch.return_value = '{"name": "my-package", "version": "1.0.0"}'
        name = extract_name_from_package_json("owner", "repo")
        assert name == "my-package", f"Expected 'my-package', got '{name}'"
        print("✓ test_extract_name_from_package_json_valid passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_package_json_invalid(self, mock_fetch):
        """Test extracting name from invalid package.json."""
        mock_fetch.return_value = "invalid json"
        name = extract_name_from_package_json("owner", "repo")
        assert name is None, f"Expected None, got '{name}'"
        print("✓ test_extract_name_from_package_json_invalid passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_readme_valid(self, mock_fetch):
        """Test extracting name from README.md."""
        mock_fetch.return_value = "# My Project\n\nThis is my project."
        name = extract_name_from_readme("owner", "repo")
        assert name == "My Project", f"Expected 'My Project', got '{name}'"
        print("✓ test_extract_name_from_readme_valid passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_readme_with_link(self, mock_fetch):
        """Test extracting name from README.md with markdown link."""
        mock_fetch.return_value = "# [My Project](https://example.com)\n\nThis is my project."
        name = extract_name_from_readme("owner", "repo")
        assert name == "My Project", f"Expected 'My Project', got '{name}'"
        print("✓ test_extract_name_from_readme_with_link passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_readme_with_formatting(self, mock_fetch):
        """Test extracting name from README.md with formatting."""
        mock_fetch.return_value = "# **My Project**\n\nThis is my project."
        name = extract_name_from_readme("owner", "repo")
        assert name == "My Project", f"Expected 'My Project', got '{name}'"
        print("✓ test_extract_name_from_readme_with_formatting passed")

    @patch('src.modules.codemeta_name.fetch_file_content')
    def test_extract_name_from_readme_not_found(self, mock_fetch):
        """Test when README.md doesn't exist."""
        mock_fetch.return_value = None
        name = extract_name_from_readme("owner", "repo")
        assert name is None, f"Expected None, got '{name}'"
        print("✓ test_extract_name_from_readme_not_found passed")

    @patch('src.modules.codemeta_name.fetch_repository_info')
    def test_extract_name_from_repository_info_valid(self, mock_fetch):
        """Test extracting name from repository info."""
        mock_fetch.return_value = {"full_name": "owner/my-repo", "name": "my-repo"}
        name = extract_name_from_repository_info("owner", "repo")
        assert name == "owner/my-repo", f"Expected 'owner/my-repo', got '{name}'"
        print("✓ test_extract_name_from_repository_info_valid passed")

    @patch('src.modules.codemeta_name.fetch_repository_info')
    def test_extract_name_from_repository_info_not_found(self, mock_fetch):
        """Test when repository info is not available."""
        mock_fetch.return_value = None
        name = extract_name_from_repository_info("owner", "repo")
        assert name is None, f"Expected None, got '{name}'"
        print("✓ test_extract_name_from_repository_info_not_found passed")

    @patch('src.modules.codemeta_name.extract_name_from_setup_py')
    @patch('src.modules.codemeta_name.extract_name_from_pyproject_toml')
    @patch('src.modules.codemeta_name.extract_name_from_package_json')
    @patch('src.modules.codemeta_name.extract_name_from_readme')
    @patch('src.modules.codemeta_name.extract_name_from_repository_info')
    @patch('src.modules.codemeta_name.extract_name_from_url')
    def test_get_priority_setup_py(self, mock_url, mock_info, mock_readme, mock_package, mock_toml, mock_setup):
        """Test that setup.py has highest priority."""
        mock_setup.return_value = "setup-name"
        mock_toml.return_value = "toml-name"
        mock_package.return_value = "package-name"
        mock_readme.return_value = "readme-name"
        mock_info.return_value = "info-name"
        mock_url.return_value = "url-name"

        result = get("https://github.com/owner/repo")
        assert result == {"name": "setup-name"}, f"Expected setup.py name, got {result}"
        print("✓ test_get_priority_setup_py passed")

    @patch('src.modules.codemeta_name.extract_name_from_setup_py')
    @patch('src.modules.codemeta_name.extract_name_from_pyproject_toml')
    @patch('src.modules.codemeta_name.extract_name_from_package_json')
    @patch('src.modules.codemeta_name.extract_name_from_readme')
    @patch('src.modules.codemeta_name.extract_name_from_repository_info')
    @patch('src.modules.codemeta_name.extract_name_from_url')
    def test_get_priority_pyproject_toml(self, mock_url, mock_info, mock_readme, mock_package, mock_toml, mock_setup):
        """Test that pyproject.toml has second priority."""
        mock_setup.return_value = None
        mock_toml.return_value = "toml-name"
        mock_package.return_value = "package-name"
        mock_readme.return_value = "readme-name"
        mock_info.return_value = "info-name"
        mock_url.return_value = "url-name"

        result = get("https://github.com/owner/repo")
        assert result == {"name": "toml-name"}, f"Expected pyproject.toml name, got {result}"
        print("✓ test_get_priority_pyproject_toml passed")

    @patch('src.modules.codemeta_name.extract_name_from_setup_py')
    @patch('src.modules.codemeta_name.extract_name_from_pyproject_toml')
    @patch('src.modules.codemeta_name.extract_name_from_package_json')
    @patch('src.modules.codemeta_name.extract_name_from_readme')
    @patch('src.modules.codemeta_name.extract_name_from_repository_info')
    @patch('src.modules.codemeta_name.extract_name_from_url')
    def test_get_priority_url_fallback(self, mock_url, mock_info, mock_readme, mock_package, mock_toml, mock_setup):
        """Test that URL is used as fallback."""
        mock_setup.return_value = None
        mock_toml.return_value = None
        mock_package.return_value = None
        mock_readme.return_value = None
        mock_info.return_value = None
        mock_url.return_value = "url-name"

        result = get("https://github.com/owner/repo")
        assert result == {"name": "url-name"}, f"Expected URL name, got {result}"
        print("✓ test_get_priority_url_fallback passed")

    @patch('src.modules.codemeta_name.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        result = get("https://example.com/invalid")
        assert result == {}, f"Expected empty dict, got {result}"
        print("✓ test_get_invalid_url passed")

    @patch('src.modules.codemeta_name.extract_name_from_setup_py')
    @patch('src.modules.codemeta_name.extract_name_from_pyproject_toml')
    @patch('src.modules.codemeta_name.extract_name_from_package_json')
    @patch('src.modules.codemeta_name.extract_name_from_readme')
    @patch('src.modules.codemeta_name.extract_name_from_repository_info')
    @patch('src.modules.codemeta_name.extract_name_from_url')
    def test_get_all_strategies_fail(self, mock_url, mock_info, mock_readme, mock_package, mock_toml, mock_setup):
        """Test when all strategies fail."""
        mock_setup.return_value = None
        mock_toml.return_value = None
        mock_package.return_value = None
        mock_readme.return_value = None
        mock_info.return_value = None
        mock_url.return_value = None

        result = get("https://github.com/owner/repo")
        assert result == {}, f"Expected empty dict, got {result}"
        print("✓ test_get_all_strategies_fail passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("RUNNING CODEMETA_NAME MODULE TESTS")
    print("=" * 80)
    print()

    test_instance = TestNameExtraction()
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]

    passed = 0
    failed = 0

    for test_method in test_methods:
        try:
            getattr(test_instance, test_method)()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_method} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_method} error: {e}")
            failed += 1

    print()
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
