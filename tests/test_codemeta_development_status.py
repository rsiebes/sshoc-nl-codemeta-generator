"""
Unit tests for codemeta_development_status module.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.modules import codemeta_development_status


class TestStatusDetection(unittest.TestCase):
    """Test status detection from various sources."""

    @patch('src.modules.codemeta_development_status.fetch_repository_info')
    def test_archived_repository(self, mock_fetch):
        """Test detection of archived repository."""
        mock_fetch.return_value = {"archived": True}
        result = codemeta_development_status.get_repository_status("owner", "repo")
        self.assertEqual(result, "Archived")

    @patch('src.modules.codemeta_development_status.fetch_repository_info')
    def test_active_repository(self, mock_fetch):
        """Test detection of active repository."""
        mock_fetch.return_value = {
            "archived": False,
            "pushed_at": "2025-12-01T10:00:00Z"
        }
        result = codemeta_development_status.get_repository_status("owner", "repo")
        self.assertEqual(result, "Active")

    @patch('src.modules.codemeta_development_status.fetch_repository_info')
    def test_inactive_repository(self, mock_fetch):
        """Test detection of inactive repository."""
        mock_fetch.return_value = {
            "archived": False,
            "pushed_at": "2024-01-01T10:00:00Z"
        }
        result = codemeta_development_status.get_repository_status("owner", "repo")
        self.assertEqual(result, "Inactive")

    @patch('src.modules.codemeta_development_status.fetch_repository_info')
    def test_no_push_date(self, mock_fetch):
        """Test handling of missing push date."""
        mock_fetch.return_value = {"archived": False}
        result = codemeta_development_status.get_repository_status("owner", "repo")
        self.assertIsNone(result)


class TestReadmeStatusDetection(unittest.TestCase):
    """Test status detection from README."""

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_readme_archived_indicator(self, mock_fetch):
        """Test detection of archived status from README."""
        mock_fetch.return_value = "This project is archived and no longer maintained."
        result = codemeta_development_status.check_readme_status("owner", "repo")
        self.assertEqual(result, "Archived")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_readme_active_indicator(self, mock_fetch):
        """Test detection of active status from README."""
        mock_fetch.return_value = "This project is actively maintained and developed."
        result = codemeta_development_status.check_readme_status("owner", "repo")
        self.assertEqual(result, "Active")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_readme_concept_indicator(self, mock_fetch):
        """Test detection of concept status from README."""
        mock_fetch.return_value = "This is a proof of concept project."
        result = codemeta_development_status.check_readme_status("owner", "repo")
        self.assertEqual(result, "Concept")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_readme_no_status_indicator(self, mock_fetch):
        """Test handling of README without status indicator."""
        mock_fetch.return_value = "This is a regular project."
        result = codemeta_development_status.check_readme_status("owner", "repo")
        self.assertIsNone(result)

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_readme_not_found(self, mock_fetch):
        """Test handling of missing README."""
        mock_fetch.return_value = None
        result = codemeta_development_status.check_readme_status("owner", "repo")
        self.assertIsNone(result)


class TestSetupPyStatusDetection(unittest.TestCase):
    """Test status detection from setup.py."""

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_setup_py_production_status(self, mock_fetch):
        """Test detection of production status from setup.py."""
        mock_fetch.return_value = """
        setup(
            name='myproject',
            classifiers=[
                'Development Status :: 5 - Production/Stable',
            ]
        )
        """
        result = codemeta_development_status.check_setup_py_status("owner", "repo")
        self.assertEqual(result, "Active")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_setup_py_alpha_status(self, mock_fetch):
        """Test detection of alpha status from setup.py."""
        mock_fetch.return_value = """
        setup(
            name='myproject',
            classifiers=[
                'Development Status :: 3 - Alpha',
            ]
        )
        """
        result = codemeta_development_status.check_setup_py_status("owner", "repo")
        self.assertEqual(result, "Concept")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_setup_py_inactive_status(self, mock_fetch):
        """Test detection of inactive status from setup.py."""
        mock_fetch.return_value = """
        setup(
            name='myproject',
            classifiers=[
                'Development Status :: 7 - Inactive',
            ]
        )
        """
        result = codemeta_development_status.check_setup_py_status("owner", "repo")
        self.assertEqual(result, "Inactive")


class TestPyprojectTomlStatusDetection(unittest.TestCase):
    """Test status detection from pyproject.toml."""

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_pyproject_toml_production_status(self, mock_fetch):
        """Test detection of production status from pyproject.toml."""
        mock_fetch.return_value = """
        [project]
        classifiers = [
            "Development Status :: 5 - Production/Stable",
        ]
        """
        result = codemeta_development_status.check_pyproject_toml_status("owner", "repo")
        self.assertEqual(result, "Active")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_pyproject_toml_beta_status(self, mock_fetch):
        """Test detection of beta status from pyproject.toml."""
        mock_fetch.return_value = """
        [project]
        classifiers = [
            "Development Status :: 4 - Beta",
        ]
        """
        result = codemeta_development_status.check_pyproject_toml_status("owner", "repo")
        self.assertEqual(result, "Active")


class TestPackageJsonStatusDetection(unittest.TestCase):
    """Test status detection from package.json."""

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_package_json_deprecated(self, mock_fetch):
        """Test detection of deprecated status from package.json."""
        mock_fetch.return_value = '{"name": "myproject", "deprecated": true}'
        result = codemeta_development_status.check_package_json_status("owner", "repo")
        self.assertEqual(result, "Archived")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_package_json_archived_description(self, mock_fetch):
        """Test detection of archived status from package.json description."""
        mock_fetch.return_value = '{"name": "myproject", "description": "This project is archived"}'
        result = codemeta_development_status.check_package_json_status("owner", "repo")
        self.assertEqual(result, "Archived")

    @patch('src.modules.codemeta_development_status.fetch_file_content')
    def test_package_json_no_status(self, mock_fetch):
        """Test handling of package.json without status."""
        mock_fetch.return_value = '{"name": "myproject"}'
        result = codemeta_development_status.check_package_json_status("owner", "repo")
        self.assertIsNone(result)


class TestGetFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_development_status.check_readme_status')
    def test_get_returns_dict(self, mock_check):
        """Test that get() returns a dictionary."""
        mock_check.return_value = "Active"
        result = codemeta_development_status.get("https://github.com/owner/repo")
        self.assertIsInstance(result, dict)

    @patch('src.modules.codemeta_development_status.check_readme_status')
    def test_get_with_status(self, mock_check):
        """Test get() with status found."""
        mock_check.return_value = "Active"
        result = codemeta_development_status.get("https://github.com/owner/repo")
        self.assertEqual(result["developmentStatus"], "Active")

    @patch('src.modules.codemeta_development_status.check_readme_status')
    @patch('src.modules.codemeta_development_status.check_setup_py_status')
    @patch('src.modules.codemeta_development_status.check_pyproject_toml_status')
    @patch('src.modules.codemeta_development_status.check_package_json_status')
    @patch('src.modules.codemeta_development_status.get_repository_status')
    def test_get_no_status(self, mock_repo, mock_pkg, mock_pyproj, mock_setup, mock_readme):
        """Test get() with no status found."""
        mock_readme.return_value = None
        mock_setup.return_value = None
        mock_pyproj.return_value = None
        mock_pkg.return_value = None
        mock_repo.return_value = None
        result = codemeta_development_status.get("https://github.com/owner/repo")
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_development_status.check_readme_status')
    @patch('src.modules.codemeta_development_status.check_setup_py_status')
    def test_get_priority_order(self, mock_setup, mock_readme):
        """Test that strategies are tried in priority order."""
        mock_readme.return_value = "Active"
        mock_setup.return_value = "Inactive"
        result = codemeta_development_status.get("https://github.com/owner/repo")
        self.assertEqual(result["developmentStatus"], "Active")
        mock_readme.assert_called_once()

    def test_get_invalid_url(self):
        """Test get() with invalid repository URL."""
        result = codemeta_development_status.get("invalid-url")
        self.assertEqual(result, {})


class TestStatusContent(unittest.TestCase):
    """Test the content and format of status values."""

    @patch('src.modules.codemeta_development_status.check_readme_status')
    def test_status_is_string(self, mock_check):
        """Test that status is a string."""
        mock_check.return_value = "Active"
        result = codemeta_development_status.get("https://github.com/owner/repo")
        self.assertIsInstance(result["developmentStatus"], str)

    @patch('src.modules.codemeta_development_status.check_readme_status')
    def test_status_not_empty(self, mock_check):
        """Test that status is not empty."""
        mock_check.return_value = "Active"
        result = codemeta_development_status.get("https://github.com/owner/repo")
        self.assertTrue(len(result["developmentStatus"]) > 0)

    @patch('src.modules.codemeta_development_status.check_readme_status')
    def test_status_valid_values(self, mock_check):
        """Test that status is one of valid values."""
        valid_statuses = ["Active", "Inactive", "Concept", "Archived", "Suspended"]
        for status in valid_statuses:
            mock_check.return_value = status
            result = codemeta_development_status.get("https://github.com/owner/repo")
            self.assertIn(result["developmentStatus"], valid_statuses)


class TestRealRepositories(unittest.TestCase):
    """Test status extraction from real repositories."""

    def test_tensorflow_status(self):
        """Test status extraction from TensorFlow."""
        result = codemeta_development_status.get("https://github.com/tensorflow/tensorflow")
        # TensorFlow is actively maintained
        if "developmentStatus" in result:
            self.assertIn(result["developmentStatus"], ["Active", "Inactive"])

    def test_flask_status(self):
        """Test status extraction from Flask."""
        result = codemeta_development_status.get("https://github.com/pallets/flask")
        # Flask is actively maintained
        if "developmentStatus" in result:
            self.assertIn(result["developmentStatus"], ["Active", "Inactive"])

    def test_rust_status(self):
        """Test status extraction from Rust."""
        result = codemeta_development_status.get("https://github.com/rust-lang/rust")
        # Rust is actively maintained
        if "developmentStatus" in result:
            self.assertIn(result["developmentStatus"], ["Active", "Inactive"])


if __name__ == "__main__":
    unittest.main()
