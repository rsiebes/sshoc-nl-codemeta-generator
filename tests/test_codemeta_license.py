#!/usr/bin/env python3
"""
Unit tests for the codemeta_license module.

This module contains tests for:
- License extraction from various sources
- SPDX identifier mapping
- License data structure validation
- Integration with the orchestrator
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.codemeta_license import (
    extract_license_from_github_api,
    extract_license_from_license_file,
    extract_license_from_setup_py,
    extract_license_from_pyproject_toml,
    extract_license_from_package_json,
    detect_license_from_content,
    get_spdx_identifier,
    get_spdx_url,
    get,
)


class TestSPDXMapping:
    """Tests for SPDX identifier mapping."""

    def test_get_spdx_identifier_mit(self):
        """Test SPDX mapping for MIT license."""
        spdx_id = get_spdx_identifier("MIT")
        assert spdx_id == "MIT", "Should map MIT to MIT"
        print("✓ test_get_spdx_identifier_mit passed")

    def test_get_spdx_identifier_apache(self):
        """Test SPDX mapping for Apache license."""
        spdx_id = get_spdx_identifier("Apache 2.0")
        assert spdx_id == "Apache-2.0", "Should map Apache 2.0 to Apache-2.0"
        print("✓ test_get_spdx_identifier_apache passed")

    def test_get_spdx_identifier_gpl3(self):
        """Test SPDX mapping for GPL v3."""
        spdx_id = get_spdx_identifier("GPLv3")
        assert spdx_id == "GPL-3.0-only", "Should map GPLv3 to GPL-3.0-only"
        print("✓ test_get_spdx_identifier_gpl3 passed")

    def test_get_spdx_identifier_case_insensitive(self):
        """Test SPDX mapping is case-insensitive."""
        spdx_id = get_spdx_identifier("mit")
        assert spdx_id == "MIT", "Should handle case-insensitive matching"
        print("✓ test_get_spdx_identifier_case_insensitive passed")

    def test_get_spdx_identifier_unknown(self):
        """Test SPDX mapping for unknown license."""
        spdx_id = get_spdx_identifier("Unknown License")
        assert spdx_id is None, "Should return None for unknown license"
        print("✓ test_get_spdx_identifier_unknown passed")

    def test_get_spdx_url(self):
        """Test SPDX URL generation."""
        url = get_spdx_url("MIT")
        assert url == "https://spdx.org/licenses/MIT", "Should generate correct SPDX URL"
        print("✓ test_get_spdx_url passed")


class TestLicenseDetection:
    """Tests for license detection from file content."""

    def test_detect_license_gpl3(self):
        """Test detecting GPL v3 from content."""
        content = "GNU GENERAL PUBLIC LICENSE Version 3"
        license_name = detect_license_from_content(content)
        assert license_name == "GPL-3.0-only", "Should detect GPL-3.0-only"
        print("✓ test_detect_license_gpl3 passed")

    def test_detect_license_mit(self):
        """Test detecting MIT from content."""
        content = "MIT License\n\nPermission is hereby granted"
        license_name = detect_license_from_content(content)
        assert license_name == "MIT", "Should detect MIT"
        print("✓ test_detect_license_mit passed")

    def test_detect_license_apache(self):
        """Test detecting Apache from content."""
        content = "Apache License Version 2.0"
        license_name = detect_license_from_content(content)
        assert license_name == "Apache-2.0", "Should detect Apache-2.0"
        print("✓ test_detect_license_apache passed")

    def test_detect_license_bsd3(self):
        """Test detecting BSD 3-Clause from content."""
        content = "BSD 3-Clause License"
        license_name = detect_license_from_content(content)
        assert license_name == "BSD-3-Clause", "Should detect BSD-3-Clause"
        print("✓ test_detect_license_bsd3 passed")

    def test_detect_license_empty_content(self):
        """Test detecting license from empty content."""
        license_name = detect_license_from_content("")
        assert license_name is None, "Should return None for empty content"
        print("✓ test_detect_license_empty_content passed")


class TestLicenseExtraction:
    """Tests for license extraction from various sources."""

    @patch('src.modules.codemeta_license.fetch_repository_info')
    def test_extract_license_from_github_api_valid(self, mock_fetch):
        """Test extracting license from GitHub API."""
        mock_fetch.return_value = {
            "license": {
                "name": "MIT License",
                "spdx_id": "MIT"
            }
        }

        license_info = extract_license_from_github_api("owner", "repo")
        assert license_info is not None, "Should extract license"
        assert license_info["name"] == "MIT License", "Should have license name"
        assert license_info["@id"] == "https://spdx.org/licenses/MIT", "Should have SPDX URL"
        print("✓ test_extract_license_from_github_api_valid passed")

    @patch('src.modules.codemeta_license.fetch_repository_info')
    def test_extract_license_from_github_api_not_found(self, mock_fetch):
        """Test when GitHub API has no license."""
        mock_fetch.return_value = {"license": None}

        license_info = extract_license_from_github_api("owner", "repo")
        assert license_info is None, "Should return None when no license"
        print("✓ test_extract_license_from_github_api_not_found passed")

    @patch('src.modules.codemeta_license.fetch_file_content')
    def test_extract_license_from_license_file_valid(self, mock_fetch):
        """Test extracting license from LICENSE file."""
        mock_fetch.return_value = "MIT License\n\nPermission is hereby granted"

        license_info = extract_license_from_license_file("owner", "repo")
        assert license_info is not None, "Should extract license"
        assert license_info["name"] == "MIT", "Should detect MIT license"
        print("✓ test_extract_license_from_license_file_valid passed")

    @patch('src.modules.codemeta_license.fetch_file_content')
    def test_extract_license_from_setup_py_valid(self, mock_fetch):
        """Test extracting license from setup.py."""
        mock_fetch.return_value = 'license="MIT"'

        license_info = extract_license_from_setup_py("owner", "repo")
        assert license_info is not None, "Should extract license"
        assert license_info["name"] == "MIT", "Should have license name"
        print("✓ test_extract_license_from_setup_py_valid passed")

    @patch('src.modules.codemeta_license.fetch_file_content')
    def test_extract_license_from_pyproject_toml_valid(self, mock_fetch):
        """Test extracting license from pyproject.toml."""
        mock_fetch.return_value = '[project]\nlicense = "MIT"'

        license_info = extract_license_from_pyproject_toml("owner", "repo")
        assert license_info is not None, "Should extract license"
        assert license_info["name"] == "MIT", "Should have license name"
        print("✓ test_extract_license_from_pyproject_toml_valid passed")

    @patch('src.modules.codemeta_license.fetch_file_content')
    def test_extract_license_from_package_json_valid(self, mock_fetch):
        """Test extracting license from package.json."""
        package_json = {"license": "MIT"}
        mock_fetch.return_value = json.dumps(package_json)

        license_info = extract_license_from_package_json("owner", "repo")
        assert license_info is not None, "Should extract license"
        assert license_info["name"] == "MIT", "Should have license name"
        print("✓ test_extract_license_from_package_json_valid passed")


class TestLicenseDataStructure:
    """Tests for license data structure validation."""

    @patch('src.modules.codemeta_license.fetch_repository_info')
    def test_license_has_required_fields(self, mock_fetch):
        """Test that extracted license has required fields."""
        mock_fetch.return_value = {
            "license": {
                "name": "MIT License",
                "spdx_id": "MIT"
            }
        }

        license_info = extract_license_from_github_api("owner", "repo")
        assert "@type" in license_info, "License should have @type"
        assert license_info["@type"] == "CreativeWork", "License type should be CreativeWork"
        assert "name" in license_info, "License should have name"
        print("✓ test_license_has_required_fields passed")

    @patch('src.modules.codemeta_license.fetch_repository_info')
    def test_license_with_spdx_has_id_field(self, mock_fetch):
        """Test that license with SPDX has @id field."""
        mock_fetch.return_value = {
            "license": {
                "name": "MIT License",
                "spdx_id": "MIT"
            }
        }

        license_info = extract_license_from_github_api("owner", "repo")
        assert "@id" in license_info, "License with SPDX should have @id"
        assert "spdx.org" in license_info["@id"], "@id should be SPDX URL"
        print("✓ test_license_with_spdx_has_id_field passed")


class TestGetFunction:
    """Tests for the main get() function."""

    @patch('src.modules.codemeta_license.extract_license_from_github_api')
    def test_get_returns_dict(self, mock_extract):
        """Test that get() returns a dictionary."""
        mock_extract.return_value = {
            "@type": "CreativeWork",
            "name": "MIT",
            "@id": "https://spdx.org/licenses/MIT"
        }

        result = get("https://github.com/owner/repo")
        assert isinstance(result, dict), "get() should return a dictionary"
        print("✓ test_get_returns_dict passed")

    @patch('src.modules.codemeta_license.extract_license_from_github_api')
    def test_get_with_license_found(self, mock_extract):
        """Test get() when license is found."""
        mock_extract.return_value = {
            "@type": "CreativeWork",
            "name": "MIT",
            "@id": "https://spdx.org/licenses/MIT"
        }

        result = get("https://github.com/owner/repo")
        assert "license" in result, "Result should contain 'license' key"
        assert isinstance(result["license"], dict), "License should be a dictionary"
        print("✓ test_get_with_license_found passed")

    @patch('src.modules.codemeta_license.extract_license_from_github_api')
    def test_get_with_no_license_found(self, mock_extract):
        """Test get() when no license is found."""
        mock_extract.return_value = None

        with patch('src.modules.codemeta_license.extract_license_from_license_file') as mock_file:
            mock_file.return_value = None

            with patch('src.modules.codemeta_license.extract_license_from_setup_py') as mock_setup:
                mock_setup.return_value = None

                with patch('src.modules.codemeta_license.extract_license_from_pyproject_toml') as mock_toml:
                    mock_toml.return_value = None

                    with patch('src.modules.codemeta_license.extract_license_from_package_json') as mock_pkg:
                        mock_pkg.return_value = None

                        result = get("https://github.com/owner/repo")
                        assert result == {}, "Should return empty dict when no license found"
        print("✓ test_get_with_no_license_found passed")

    def test_get_with_invalid_url(self):
        """Test get() with invalid URL."""
        result = get("invalid-url")
        assert result == {}, "Should return empty dict for invalid URL"
        print("✓ test_get_with_invalid_url passed")


def run_all_tests():
    """Run all license module tests."""
    print("=" * 80)
    print("RUNNING CODEMETA_LICENSE MODULE TESTS")
    print("=" * 80)
    print()

    test_classes = [
        TestSPDXMapping,
        TestLicenseDetection,
        TestLicenseExtraction,
        TestLicenseDataStructure,
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
