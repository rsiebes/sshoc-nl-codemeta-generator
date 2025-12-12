"""
Unit tests for codemeta_operating_system module.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.modules import codemeta_operating_system


class TestOSDetectionFromReadme(unittest.TestCase):
    """Test OS detection from README."""

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_linux_from_readme(self, mock_fetch):
        """Test detection of Linux from README."""
        mock_fetch.return_value = "Supports Linux and macOS"
        result = codemeta_operating_system.detect_os_from_readme("owner", "repo")
        
        self.assertIn("Linux", result)
        self.assertIn("macOS", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_windows_from_readme(self, mock_fetch):
        """Test detection of Windows from README."""
        mock_fetch.return_value = "Works on Windows, macOS, and Linux"
        result = codemeta_operating_system.detect_os_from_readme("owner", "repo")
        
        self.assertIn("Windows", result)
        self.assertIn("macOS", result)
        self.assertIn("Linux", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_unix_from_readme(self, mock_fetch):
        """Test detection of Unix from README."""
        mock_fetch.return_value = "POSIX compliant Unix system"
        result = codemeta_operating_system.detect_os_from_readme("owner", "repo")
        
        self.assertIn("Unix", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_no_os_in_readme(self, mock_fetch):
        """Test when no OS is mentioned in README."""
        mock_fetch.return_value = "This is a generic project"
        result = codemeta_operating_system.detect_os_from_readme("owner", "repo")
        
        self.assertEqual(result, [])

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_missing_readme(self, mock_fetch):
        """Test handling of missing README."""
        mock_fetch.return_value = None
        result = codemeta_operating_system.detect_os_from_readme("owner", "repo")
        
        self.assertEqual(result, [])


class TestOSDetectionFromCI(unittest.TestCase):
    """Test OS detection from CI/CD configuration."""

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_from_github_actions(self, mock_fetch):
        """Test detection from GitHub Actions workflow."""
        workflow = """
        strategy:
          matrix:
            os: [ubuntu-latest, macos-latest, windows-latest]
        """
        mock_fetch.return_value = workflow
        result = codemeta_operating_system.detect_os_from_ci_config("owner", "repo")
        
        self.assertIn("Linux", result)
        self.assertIn("macOS", result)
        self.assertIn("Windows", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_from_travis_ci(self, mock_fetch):
        """Test detection from Travis CI config."""
        travis = """
        os:
          - linux
          - osx
        """
        # Mock returns: main.yml (None), ci.yml (None), travis (content), appveyor (None), circleci (None)
        mock_fetch.side_effect = [None, None, travis, None, None]
        result = codemeta_operating_system.detect_os_from_ci_config("owner", "repo")
        
        self.assertIn("Linux", result)
        self.assertIn("macOS", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_from_appveyor(self, mock_fetch):
        """Test detection from AppVeyor config."""
        appveyor = """
        image:
          - Visual Studio 2019
        """
        # Mock returns: main.yml (None), ci.yml (None), travis (None), appveyor (content), circleci (None)
        mock_fetch.side_effect = [None, None, None, appveyor, None]
        result = codemeta_operating_system.detect_os_from_ci_config("owner", "repo")
        
        self.assertIn("Windows", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_no_ci_config(self, mock_fetch):
        """Test when no CI config is found."""
        mock_fetch.return_value = None
        result = codemeta_operating_system.detect_os_from_ci_config("owner", "repo")
        
        self.assertEqual(result, [])


class TestOSDetectionFromSetup(unittest.TestCase):
    """Test OS detection from setup files."""

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_from_setup_py(self, mock_fetch):
        """Test detection from setup.py."""
        setup = """
        classifiers=[
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS',
            'Operating System :: POSIX :: Linux',
        ]
        """
        # First call for setup.py returns content
        mock_fetch.return_value = setup
        result = codemeta_operating_system.detect_os_from_setup_files("owner", "repo")
        
        self.assertIn("Windows", result)
        self.assertIn("macOS", result)
        self.assertIn("Linux", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_detect_from_pyproject_toml(self, mock_fetch):
        """Test detection from pyproject.toml."""
        pyproject = """
        classifiers = [
            "Operating System :: Microsoft :: Windows",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
        ]
        """
        # First call for setup.py returns None
        # Second call for pyproject.toml returns content
        # Third call for Dockerfile returns None
        mock_fetch.side_effect = [None, pyproject, None]
        result = codemeta_operating_system.detect_os_from_setup_files("owner", "repo")
        
        self.assertIn("Windows", result)
        self.assertIn("macOS", result)
        self.assertIn("Linux", result)

    @patch('src.modules.codemeta_operating_system.fetch_file_content')
    def test_no_setup_files(self, mock_fetch):
        """Test when no setup files are found."""
        mock_fetch.return_value = None
        result = codemeta_operating_system.detect_os_from_setup_files("owner", "repo")
        
        self.assertEqual(result, [])


class TestOSExtraction(unittest.TestCase):
    """Test main OS extraction."""

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_basic_os_extraction(self, mock_setup, mock_ci, mock_readme):
        """Test extraction of basic OS information."""
        mock_readme.return_value = ["Linux", "macOS"]
        mock_ci.return_value = ["Windows"]
        mock_setup.return_value = []
        
        result = codemeta_operating_system.get("https://github.com/owner/repo")
        
        self.assertIn("operatingSystem", result)
        self.assertEqual(set(result["operatingSystem"]), {"Linux", "macOS", "Windows"})

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_no_os_detected(self, mock_setup, mock_ci, mock_readme):
        """Test handling of no OS detected."""
        mock_readme.return_value = []
        mock_ci.return_value = []
        mock_setup.return_value = []
        
        result = codemeta_operating_system.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_invalid_url_handling(self, mock_setup, mock_ci, mock_readme):
        """Test handling of invalid repository URL."""
        result = codemeta_operating_system.get("invalid-url")
        
        self.assertEqual(result, {})


class TestOSContent(unittest.TestCase):
    """Test OS content validation."""

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_os_is_list(self, mock_setup, mock_ci, mock_readme):
        """Test that OS is a list."""
        mock_readme.return_value = ["Linux"]
        mock_ci.return_value = []
        mock_setup.return_value = []
        
        result = codemeta_operating_system.get("https://github.com/owner/repo")
        
        self.assertIn("operatingSystem", result)
        self.assertIsInstance(result["operatingSystem"], list)

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_os_not_empty(self, mock_setup, mock_ci, mock_readme):
        """Test that OS list is not empty."""
        mock_readme.return_value = ["Linux"]
        mock_ci.return_value = []
        mock_setup.return_value = []
        
        result = codemeta_operating_system.get("https://github.com/owner/repo")
        
        self.assertIn("operatingSystem", result)
        self.assertTrue(len(result["operatingSystem"]) > 0)

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_os_sorted(self, mock_setup, mock_ci, mock_readme):
        """Test that OS list is sorted."""
        mock_readme.return_value = ["Windows", "Linux"]
        mock_ci.return_value = ["macOS"]
        mock_setup.return_value = []
        
        result = codemeta_operating_system.get("https://github.com/owner/repo")
        
        self.assertIn("operatingSystem", result)
        self.assertEqual(result["operatingSystem"], sorted(result["operatingSystem"]))


class TestRealRepositories(unittest.TestCase):
    """Test OS detection from real repositories."""

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_tensorflow_os(self, mock_setup, mock_ci, mock_readme):
        """Test OS detection from TensorFlow."""
        mock_readme.return_value = ["Linux", "macOS", "Windows"]
        mock_ci.return_value = ["Linux", "macOS", "Windows"]
        mock_setup.return_value = []
        
        result = codemeta_operating_system.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("operatingSystem", result)
        self.assertIn("Linux", result["operatingSystem"])
        self.assertIn("Windows", result["operatingSystem"])

    @patch('src.modules.codemeta_operating_system.detect_os_from_readme')
    @patch('src.modules.codemeta_operating_system.detect_os_from_ci_config')
    @patch('src.modules.codemeta_operating_system.detect_os_from_setup_files')
    def test_flask_os(self, mock_setup, mock_ci, mock_readme):
        """Test OS detection from Flask."""
        mock_readme.return_value = ["Linux", "macOS", "Windows"]
        mock_ci.return_value = ["Linux"]
        mock_setup.return_value = ["Unix"]
        
        result = codemeta_operating_system.get("https://github.com/pallets/flask")
        
        self.assertIn("operatingSystem", result)
        self.assertIn("Linux", result["operatingSystem"])


if __name__ == '__main__':
    unittest.main()
