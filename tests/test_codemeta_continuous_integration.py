"""
Unit tests for the CodeMeta Continuous Integration Module
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_continuous_integration


class TestCIPlatformDetection(unittest.TestCase):
    """Test CI platform detection."""

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_github_actions(self, mock_fetch):
        """Test detection of GitHub Actions."""
        mock_fetch.side_effect = lambda owner, repo, path: "workflows" if path == ".github/workflows" else None
        
        result = codemeta_continuous_integration.detect_ci_platforms("owner", "repo")
        
        self.assertIn("GitHub Actions", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_travis_ci(self, mock_fetch):
        """Test detection of Travis CI."""
        mock_fetch.side_effect = lambda owner, repo, path: "travis config" if path == ".travis.yml" else None
        
        result = codemeta_continuous_integration.detect_ci_platforms("owner", "repo")
        
        self.assertIn("Travis CI", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_circle_ci(self, mock_fetch):
        """Test detection of Circle CI."""
        mock_fetch.side_effect = lambda owner, repo, path: "circle config" if path == ".circleci/config.yml" else None
        
        result = codemeta_continuous_integration.detect_ci_platforms("owner", "repo")
        
        self.assertIn("Circle CI", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_multiple_platforms(self, mock_fetch):
        """Test detection of multiple CI platforms."""
        def side_effect(owner, repo, path):
            if path == ".github/workflows":
                return "workflows"
            elif path == ".travis.yml":
                return "travis"
            elif path == ".circleci/config.yml":
                return "circle"
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = codemeta_continuous_integration.detect_ci_platforms("owner", "repo")
        
        self.assertIn("GitHub Actions", result)
        self.assertIn("Travis CI", result)
        self.assertIn("Circle CI", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_no_ci_platforms(self, mock_fetch):
        """Test when no CI platforms are found."""
        mock_fetch.return_value = None
        
        result = codemeta_continuous_integration.detect_ci_platforms("owner", "repo")
        
        self.assertEqual(result, [])


class TestTestingFrameworkDetection(unittest.TestCase):
    """Test testing framework detection."""

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_pytest(self, mock_fetch):
        """Test detection of pytest."""
        mock_fetch.side_effect = lambda owner, repo, path: "pytest==7.0.0" if path == "requirements-dev.txt" else None
        
        result = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
        
        self.assertIn("pytest", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_jest(self, mock_fetch):
        """Test detection of Jest."""
        package_json = '{"devDependencies": {"jest": "^27.0.0"}}'
        mock_fetch.side_effect = lambda owner, repo, path: package_json if path == "package.json" else None
        
        result = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
        
        self.assertIn("Jest", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_junit(self, mock_fetch):
        """Test detection of JUnit."""
        pom_xml = "<dependency><artifactId>junit</artifactId></dependency>"
        mock_fetch.side_effect = lambda owner, repo, path: pom_xml if path == "pom.xml" else None
        
        result = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
        
        self.assertIn("JUnit", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_rspec(self, mock_fetch):
        """Test detection of RSpec."""
        gemfile = "gem 'rspec'"
        mock_fetch.side_effect = lambda owner, repo, path: gemfile if path == "Gemfile" else None
        
        result = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
        
        self.assertIn("RSpec", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_multiple_frameworks(self, mock_fetch):
        """Test detection of multiple testing frameworks."""
        def side_effect(owner, repo, path):
            if path == "requirements-dev.txt":
                return "pytest==7.0.0\nnosetests==1.3.7"
            elif path == "package.json":
                return '{"devDependencies": {"jest": "^27.0.0"}}'
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
        
        self.assertIn("pytest", result)
        self.assertIn("Jest", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_no_testing_frameworks(self, mock_fetch):
        """Test when no testing frameworks are found."""
        mock_fetch.return_value = None
        
        result = codemeta_continuous_integration.detect_testing_frameworks("owner", "repo")
        
        self.assertEqual(result, [])


class TestCoverageToolDetection(unittest.TestCase):
    """Test coverage tool detection."""

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_coverage_py(self, mock_fetch):
        """Test detection of coverage.py."""
        mock_fetch.side_effect = lambda owner, repo, path: "[run]" if path == ".coveragerc" else None
        
        result = codemeta_continuous_integration.detect_coverage_tools("owner", "repo")
        
        self.assertIn("coverage.py", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_codecov(self, mock_fetch):
        """Test detection of Codecov."""
        mock_fetch.side_effect = lambda owner, repo, path: "codecov:" if path == "codecov.yml" else None
        
        result = codemeta_continuous_integration.detect_coverage_tools("owner", "repo")
        
        self.assertIn("Codecov", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_sonarqube(self, mock_fetch):
        """Test detection of SonarQube."""
        mock_fetch.side_effect = lambda owner, repo, path: "sonar.projectKey=com.example" if path == "sonar-project.properties" else None
        
        result = codemeta_continuous_integration.detect_coverage_tools("owner", "repo")
        
        self.assertIn("SonarQube", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_detect_multiple_coverage_tools(self, mock_fetch):
        """Test detection of multiple coverage tools."""
        def side_effect(owner, repo, path):
            if path == ".coveragerc":
                return "[run]"
            elif path == "codecov.yml":
                return "codecov:"
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = codemeta_continuous_integration.detect_coverage_tools("owner", "repo")
        
        self.assertIn("coverage.py", result)
        self.assertIn("Codecov", result)

    @patch('src.modules.codemeta_continuous_integration.fetch_file_content')
    def test_no_coverage_tools(self, mock_fetch):
        """Test when no coverage tools are found."""
        mock_fetch.return_value = None
        
        result = codemeta_continuous_integration.detect_coverage_tools("owner", "repo")
        
        self.assertEqual(result, [])


class TestCIInfoExtraction(unittest.TestCase):
    """Test CI info extraction."""

    @patch('src.modules.codemeta_continuous_integration.detect_coverage_tools')
    @patch('src.modules.codemeta_continuous_integration.detect_testing_frameworks')
    @patch('src.modules.codemeta_continuous_integration.detect_ci_platforms')
    def test_extract_ci_info(self, mock_platforms, mock_frameworks, mock_coverage):
        """Test extraction of CI information."""
        mock_platforms.return_value = ["GitHub Actions"]
        mock_frameworks.return_value = ["pytest"]
        mock_coverage.return_value = ["coverage.py"]
        
        result = codemeta_continuous_integration.extract_ci_info("owner", "repo")
        
        self.assertIn("platforms", result)
        self.assertIn("testingFrameworks", result)
        self.assertIn("coverageTools", result)
        self.assertEqual(result["platforms"], ["GitHub Actions"])
        self.assertEqual(result["testingFrameworks"], ["pytest"])
        self.assertEqual(result["coverageTools"], ["coverage.py"])

    @patch('src.modules.codemeta_continuous_integration.detect_coverage_tools')
    @patch('src.modules.codemeta_continuous_integration.detect_testing_frameworks')
    @patch('src.modules.codemeta_continuous_integration.detect_ci_platforms')
    def test_extract_empty_ci_info(self, mock_platforms, mock_frameworks, mock_coverage):
        """Test extraction when no CI info found."""
        mock_platforms.return_value = []
        mock_frameworks.return_value = []
        mock_coverage.return_value = []
        
        result = codemeta_continuous_integration.extract_ci_info("owner", "repo")
        
        self.assertEqual(result["platforms"], [])
        self.assertEqual(result["testingFrameworks"], [])
        self.assertEqual(result["coverageTools"], [])


class TestCIInfoFormatting(unittest.TestCase):
    """Test CI info formatting."""

    def test_format_ci_info_all_fields(self):
        """Test formatting with all fields."""
        ci_info = {
            "platforms": ["GitHub Actions", "Travis CI"],
            "testingFrameworks": ["pytest", "Jest"],
            "coverageTools": ["coverage.py", "Codecov"]
        }
        
        result = codemeta_continuous_integration.format_ci_info(ci_info)
        
        self.assertIn("GitHub Actions", result)
        self.assertIn("pytest", result)
        self.assertIn("coverage.py", result)

    def test_format_ci_info_partial_fields(self):
        """Test formatting with partial fields."""
        ci_info = {
            "platforms": ["GitHub Actions"],
            "testingFrameworks": [],
            "coverageTools": []
        }
        
        result = codemeta_continuous_integration.format_ci_info(ci_info)
        
        self.assertIn("GitHub Actions", result)

    def test_format_ci_info_empty(self):
        """Test formatting with empty fields."""
        ci_info = {
            "platforms": [],
            "testingFrameworks": [],
            "coverageTools": []
        }
        
        result = codemeta_continuous_integration.format_ci_info(ci_info)
        
        self.assertIsNone(result)


class TestMainCIFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_continuous_integration.extract_ci_info')
    @patch('src.modules.codemeta_continuous_integration.parse_repository_url')
    def test_get_ci_info(self, mock_parse, mock_extract):
        """Test get() function with CI info."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": ["GitHub Actions"],
            "testingFrameworks": ["pytest"],
            "coverageTools": ["coverage.py"]
        }
        
        result = codemeta_continuous_integration.get("https://github.com/owner/repo")
        
        self.assertIn("continuousIntegration", result)
        self.assertEqual(result["continuousIntegration"]["platforms"], ["GitHub Actions"])

    @patch('src.modules.codemeta_continuous_integration.extract_ci_info')
    @patch('src.modules.codemeta_continuous_integration.parse_repository_url')
    def test_get_no_ci_info(self, mock_parse, mock_extract):
        """Test get() function with no CI info."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": [],
            "testingFrameworks": [],
            "coverageTools": []
        }
        
        result = codemeta_continuous_integration.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_continuous_integration.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_continuous_integration.get("invalid-url")
        
        self.assertEqual(result, {})


class TestCIDataValidation(unittest.TestCase):
    """Test CI data validation."""

    @patch('src.modules.codemeta_continuous_integration.extract_ci_info')
    @patch('src.modules.codemeta_continuous_integration.parse_repository_url')
    def test_ci_info_is_dict(self, mock_parse, mock_extract):
        """Test that CI info is a dictionary."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": ["GitHub Actions"],
            "testingFrameworks": ["pytest"],
            "coverageTools": []
        }
        
        result = codemeta_continuous_integration.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result.get("continuousIntegration"), dict)

    @patch('src.modules.codemeta_continuous_integration.extract_ci_info')
    @patch('src.modules.codemeta_continuous_integration.parse_repository_url')
    def test_ci_platforms_is_list(self, mock_parse, mock_extract):
        """Test that platforms is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": ["GitHub Actions"],
            "testingFrameworks": [],
            "coverageTools": []
        }
        
        result = codemeta_continuous_integration.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result["continuousIntegration"]["platforms"], list)

    @patch('src.modules.codemeta_continuous_integration.extract_ci_info')
    @patch('src.modules.codemeta_continuous_integration.parse_repository_url')
    def test_ci_frameworks_is_list(self, mock_parse, mock_extract):
        """Test that testing frameworks is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": [],
            "testingFrameworks": ["pytest", "Jest"],
            "coverageTools": []
        }
        
        result = codemeta_continuous_integration.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result["continuousIntegration"]["testingFrameworks"], list)


if __name__ == '__main__':
    unittest.main()
