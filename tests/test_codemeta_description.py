#!/usr/bin/env python3
"""
Unit tests for the codemeta_description module.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_description import (
    extract_description_from_repository_info,
    extract_description_from_readme,
    extract_description_from_setup_py,
    extract_description_from_setup_cfg,
    extract_description_from_pyproject_toml,
    extract_description_from_package_json,
    get
)


class TestDescriptionExtraction:
    """Test suite for description extraction functions."""

    @patch('src.modules.codemeta_description.fetch_repository_info')
    def test_extract_description_from_repository_info_valid(self, mock_fetch):
        """Test extracting description from repository info."""
        mock_fetch.return_value = {"description": "This is a test project"}
        description = extract_description_from_repository_info("owner", "repo")
        assert description == "This is a test project", f"Expected 'This is a test project', got '{description}'"
        print("✓ test_extract_description_from_repository_info_valid passed")

    @patch('src.modules.codemeta_description.fetch_repository_info')
    def test_extract_description_from_repository_info_empty(self, mock_fetch):
        """Test when repository description is empty."""
        mock_fetch.return_value = {"description": ""}
        description = extract_description_from_repository_info("owner", "repo")
        assert description is None, f"Expected None, got '{description}'"
        print("✓ test_extract_description_from_repository_info_empty passed")

    @patch('src.modules.codemeta_description.fetch_repository_info')
    def test_extract_description_from_repository_info_not_found(self, mock_fetch):
        """Test when repository info is not available."""
        mock_fetch.return_value = None
        description = extract_description_from_repository_info("owner", "repo")
        assert description is None, f"Expected None, got '{description}'"
        print("✓ test_extract_description_from_repository_info_not_found passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_readme_valid(self, mock_fetch):
        """Test extracting description from README.md."""
        readme_content = """# My Project

This is a detailed description of my project.
It explains what the project does.

## Installation

To install this project...
"""
        mock_fetch.return_value = readme_content
        description = extract_description_from_readme("owner", "repo")
        assert description is not None, "Expected description, got None"
        assert "detailed description" in description.lower(), f"Expected 'detailed description' in '{description}'"
        print("✓ test_extract_description_from_readme_valid passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_readme_multiline(self, mock_fetch):
        """Test extracting multiline description from README.md."""
        readme_content = """# My Project

This is the first line of description.
This is the second line of description.
This is the third line of description.

## Installation

To install...
"""
        mock_fetch.return_value = readme_content
        description = extract_description_from_readme("owner", "repo")
        assert description is not None, "Expected description, got None"
        assert "first line" in description, f"Expected 'first line' in '{description}'"
        assert "second line" in description, f"Expected 'second line' in '{description}'"
        print("✓ test_extract_description_from_readme_multiline passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_readme_not_found(self, mock_fetch):
        """Test when README.md doesn't exist."""
        mock_fetch.return_value = None
        description = extract_description_from_readme("owner", "repo")
        assert description is None, f"Expected None, got '{description}'"
        print("✓ test_extract_description_from_readme_not_found passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_setup_py_valid(self, mock_fetch):
        """Test extracting description from setup.py."""
        setup_content = 'setup(name="my-package", long_description="This is a test package")'
        mock_fetch.return_value = setup_content
        description = extract_description_from_setup_py("owner", "repo")
        assert description == "This is a test package", f"Expected 'This is a test package', got '{description}'"
        print("✓ test_extract_description_from_setup_py_valid passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_setup_py_description_field(self, mock_fetch):
        """Test extracting description field from setup.py."""
        setup_content = 'setup(name="my-package", description="A short description")'
        mock_fetch.return_value = setup_content
        description = extract_description_from_setup_py("owner", "repo")
        assert description == "A short description", f"Expected 'A short description', got '{description}'"
        print("✓ test_extract_description_from_setup_py_description_field passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_setup_cfg_valid(self, mock_fetch):
        """Test extracting description from setup.cfg."""
        setup_cfg_content = """[metadata]
name = my-package
long_description = This is a test package
"""
        mock_fetch.return_value = setup_cfg_content
        description = extract_description_from_setup_cfg("owner", "repo")
        assert description is not None, "Expected description, got None"
        assert "test package" in description, f"Expected 'test package' in '{description}'"
        print("✓ test_extract_description_from_setup_cfg_valid passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_pyproject_toml_valid(self, mock_fetch):
        """Test extracting description from pyproject.toml."""
        pyproject_content = """[project]
name = "my-package"
description = "This is a test package"
"""
        mock_fetch.return_value = pyproject_content
        description = extract_description_from_pyproject_toml("owner", "repo")
        assert description == "This is a test package", f"Expected 'This is a test package', got '{description}'"
        print("✓ test_extract_description_from_pyproject_toml_valid passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_package_json_valid(self, mock_fetch):
        """Test extracting description from package.json."""
        package_json_content = '{"name": "my-package", "description": "This is a test package"}'
        mock_fetch.return_value = package_json_content
        description = extract_description_from_package_json("owner", "repo")
        assert description == "This is a test package", f"Expected 'This is a test package', got '{description}'"
        print("✓ test_extract_description_from_package_json_valid passed")

    @patch('src.modules.codemeta_description.fetch_file_content')
    def test_extract_description_from_package_json_invalid(self, mock_fetch):
        """Test extracting description from invalid package.json."""
        mock_fetch.return_value = "invalid json"
        description = extract_description_from_package_json("owner", "repo")
        assert description is None, f"Expected None, got '{description}'"
        print("✓ test_extract_description_from_package_json_invalid passed")

    @patch('src.modules.codemeta_description.extract_description_from_repository_info')
    @patch('src.modules.codemeta_description.extract_description_from_readme')
    @patch('src.modules.codemeta_description.extract_description_from_setup_py')
    @patch('src.modules.codemeta_description.extract_description_from_setup_cfg')
    @patch('src.modules.codemeta_description.extract_description_from_pyproject_toml')
    @patch('src.modules.codemeta_description.extract_description_from_package_json')
    def test_get_priority_repository_info(self, mock_pkg, mock_toml, mock_cfg, mock_setup, mock_readme, mock_info):
        """Test that repository info has highest priority."""
        mock_info.return_value = "info-description"
        mock_readme.return_value = "readme-description"
        mock_setup.return_value = "setup-description"
        mock_cfg.return_value = "cfg-description"
        mock_toml.return_value = "toml-description"
        mock_pkg.return_value = "pkg-description"

        result = get("https://github.com/owner/repo")
        assert result == {"description": "info-description"}, f"Expected info description, got {result}"
        print("✓ test_get_priority_repository_info passed")

    @patch('src.modules.codemeta_description.extract_description_from_repository_info')
    @patch('src.modules.codemeta_description.extract_description_from_readme')
    @patch('src.modules.codemeta_description.extract_description_from_setup_py')
    @patch('src.modules.codemeta_description.extract_description_from_setup_cfg')
    @patch('src.modules.codemeta_description.extract_description_from_pyproject_toml')
    @patch('src.modules.codemeta_description.extract_description_from_package_json')
    def test_get_priority_readme(self, mock_pkg, mock_toml, mock_cfg, mock_setup, mock_readme, mock_info):
        """Test that README has second priority."""
        mock_info.return_value = None
        mock_readme.return_value = "readme-description"
        mock_setup.return_value = "setup-description"
        mock_cfg.return_value = "cfg-description"
        mock_toml.return_value = "toml-description"
        mock_pkg.return_value = "pkg-description"

        result = get("https://github.com/owner/repo")
        assert result == {"description": "readme-description"}, f"Expected readme description, got {result}"
        print("✓ test_get_priority_readme passed")

    @patch('src.modules.codemeta_description.extract_description_from_repository_info')
    @patch('src.modules.codemeta_description.extract_description_from_readme')
    @patch('src.modules.codemeta_description.extract_description_from_setup_py')
    @patch('src.modules.codemeta_description.extract_description_from_setup_cfg')
    @patch('src.modules.codemeta_description.extract_description_from_pyproject_toml')
    @patch('src.modules.codemeta_description.extract_description_from_package_json')
    def test_get_priority_package_json_fallback(self, mock_pkg, mock_toml, mock_cfg, mock_setup, mock_readme, mock_info):
        """Test that package.json is used as fallback."""
        mock_info.return_value = None
        mock_readme.return_value = None
        mock_setup.return_value = None
        mock_cfg.return_value = None
        mock_toml.return_value = None
        mock_pkg.return_value = "pkg-description"

        result = get("https://github.com/owner/repo")
        assert result == {"description": "pkg-description"}, f"Expected package.json description, got {result}"
        print("✓ test_get_priority_package_json_fallback passed")

    @patch('src.modules.codemeta_description.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        result = get("https://example.com/invalid")
        assert result == {}, f"Expected empty dict, got {result}"
        print("✓ test_get_invalid_url passed")

    @patch('src.modules.codemeta_description.extract_description_from_repository_info')
    @patch('src.modules.codemeta_description.extract_description_from_readme')
    @patch('src.modules.codemeta_description.extract_description_from_setup_py')
    @patch('src.modules.codemeta_description.extract_description_from_setup_cfg')
    @patch('src.modules.codemeta_description.extract_description_from_pyproject_toml')
    @patch('src.modules.codemeta_description.extract_description_from_package_json')
    def test_get_all_strategies_fail(self, mock_pkg, mock_toml, mock_cfg, mock_setup, mock_readme, mock_info):
        """Test when all strategies fail."""
        mock_info.return_value = None
        mock_readme.return_value = None
        mock_setup.return_value = None
        mock_cfg.return_value = None
        mock_toml.return_value = None
        mock_pkg.return_value = None

        result = get("https://github.com/owner/repo")
        assert result == {}, f"Expected empty dict, got {result}"
        print("✓ test_get_all_strategies_fail passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("RUNNING CODEMETA_DESCRIPTION MODULE TESTS")
    print("=" * 80)
    print()

    test_instance = TestDescriptionExtraction()
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
