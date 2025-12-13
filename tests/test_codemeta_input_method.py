"""
Unit tests for the CodeMeta Input Method Module
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_input_method


class TestCLIDetection(unittest.TestCase):
    """Test CLI interface detection."""

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_cli_from_setup_py(self, mock_fetch):
        """Test CLI detection from setup.py."""
        setup_py = "install_requires=['click>=7.0']"
        mock_fetch.side_effect = lambda owner, repo, path: setup_py if path == "setup.py" else None
        
        result = codemeta_input_method.detect_cli_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_cli_from_pyproject_toml(self, mock_fetch):
        """Test CLI detection from pyproject.toml."""
        pyproject = "dependencies = ['typer>=0.3.0']"
        mock_fetch.side_effect = lambda owner, repo, path: pyproject if path == "pyproject.toml" else None
        
        result = codemeta_input_method.detect_cli_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_cli_from_package_json(self, mock_fetch):
        """Test CLI detection from package.json."""
        package_json = '{"dependencies": {"commander": "^9.0.0"}}'
        mock_fetch.side_effect = lambda owner, repo, path: package_json if path == "package.json" else None
        
        result = codemeta_input_method.detect_cli_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_no_cli_interface(self, mock_fetch):
        """Test when no CLI interface is detected."""
        mock_fetch.return_value = None
        
        result = codemeta_input_method.detect_cli_interface("owner", "repo")
        
        self.assertFalse(result)


class TestGUIDetection(unittest.TestCase):
    """Test GUI interface detection."""

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_gui_from_setup_py(self, mock_fetch):
        """Test GUI detection from setup.py."""
        setup_py = "install_requires=['PyQt5>=5.15']"
        mock_fetch.side_effect = lambda owner, repo, path: setup_py if path == "setup.py" else None
        
        result = codemeta_input_method.detect_gui_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_gui_from_pyproject_toml(self, mock_fetch):
        """Test GUI detection from pyproject.toml."""
        pyproject = "dependencies = ['pyside2>=5.15']"
        mock_fetch.side_effect = lambda owner, repo, path: pyproject if path == "pyproject.toml" else None
        
        result = codemeta_input_method.detect_gui_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_gui_from_package_json(self, mock_fetch):
        """Test GUI detection from package.json."""
        package_json = '{"dependencies": {"electron": "^13.0.0"}}'
        mock_fetch.side_effect = lambda owner, repo, path: package_json if path == "package.json" else None
        
        result = codemeta_input_method.detect_gui_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_no_gui_interface(self, mock_fetch):
        """Test when no GUI interface is detected."""
        mock_fetch.return_value = None
        
        result = codemeta_input_method.detect_gui_interface("owner", "repo")
        
        self.assertFalse(result)


class TestWebDetection(unittest.TestCase):
    """Test web interface detection."""

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_web_from_setup_py(self, mock_fetch):
        """Test web detection from setup.py."""
        setup_py = "install_requires=['flask>=1.0']"
        mock_fetch.side_effect = lambda owner, repo, path: setup_py if path == "setup.py" else None
        
        result = codemeta_input_method.detect_web_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_web_from_pyproject_toml(self, mock_fetch):
        """Test web detection from pyproject.toml."""
        pyproject = "dependencies = ['django>=3.0']"
        mock_fetch.side_effect = lambda owner, repo, path: pyproject if path == "pyproject.toml" else None
        
        result = codemeta_input_method.detect_web_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_web_from_package_json(self, mock_fetch):
        """Test web detection from package.json."""
        package_json = '{"dependencies": {"react": "^17.0.0"}}'
        mock_fetch.side_effect = lambda owner, repo, path: package_json if path == "package.json" else None
        
        result = codemeta_input_method.detect_web_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_no_web_interface(self, mock_fetch):
        """Test when no web interface is detected."""
        mock_fetch.return_value = None
        
        result = codemeta_input_method.detect_web_interface("owner", "repo")
        
        self.assertFalse(result)


class TestAPIDetection(unittest.TestCase):
    """Test API interface detection."""

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_api_from_readme(self, mock_fetch):
        """Test API detection from README."""
        readme = "This library provides a REST API for data access."
        mock_fetch.side_effect = lambda owner, repo, path: readme if path == "README.md" else None
        
        result = codemeta_input_method.detect_api_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_api_from_setup_py(self, mock_fetch):
        """Test API detection from setup.py."""
        setup_py = "install_requires=['fastapi>=0.63']"
        mock_fetch.side_effect = lambda owner, repo, path: setup_py if path == "setup.py" else None
        
        result = codemeta_input_method.detect_api_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_api_from_openapi(self, mock_fetch):
        """Test API detection from OpenAPI spec."""
        openapi = "openapi: 3.0.0"
        mock_fetch.side_effect = lambda owner, repo, path: openapi if path == "openapi.yaml" else None
        
        result = codemeta_input_method.detect_api_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_no_api_interface(self, mock_fetch):
        """Test when no API interface is detected."""
        mock_fetch.return_value = None
        
        result = codemeta_input_method.detect_api_interface("owner", "repo")
        
        self.assertFalse(result)


class TestLibraryDetection(unittest.TestCase):
    """Test library/SDK interface detection."""

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_library_from_readme(self, mock_fetch):
        """Test library detection from README."""
        readme = "A Python library for data processing. Import it with: from mylib import process"
        mock_fetch.side_effect = lambda owner, repo, path: readme if path == "README.md" else None
        
        result = codemeta_input_method.detect_library_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_detect_library_from_setup_py(self, mock_fetch):
        """Test library detection from setup.py."""
        setup_py = "packages=find_packages()"
        mock_fetch.side_effect = lambda owner, repo, path: setup_py if path == "setup.py" else None
        
        result = codemeta_input_method.detect_library_interface("owner", "repo")
        
        self.assertTrue(result)

    @patch('src.modules.codemeta_input_method.fetch_file_content')
    def test_no_library_interface(self, mock_fetch):
        """Test when no library interface is detected."""
        mock_fetch.return_value = None
        
        result = codemeta_input_method.detect_library_interface("owner", "repo")
        
        self.assertFalse(result)


class TestGetInputMethods(unittest.TestCase):
    """Test the main get_input_methods function."""

    @patch('src.modules.codemeta_input_method.detect_library_interface')
    @patch('src.modules.codemeta_input_method.detect_api_interface')
    @patch('src.modules.codemeta_input_method.detect_web_interface')
    @patch('src.modules.codemeta_input_method.detect_gui_interface')
    @patch('src.modules.codemeta_input_method.detect_cli_interface')
    def test_get_all_methods(self, mock_cli, mock_gui, mock_web, mock_api, mock_lib):
        """Test getting all input methods."""
        mock_cli.return_value = True
        mock_gui.return_value = True
        mock_web.return_value = True
        mock_api.return_value = True
        mock_lib.return_value = True
        
        result = codemeta_input_method.get_input_methods("owner", "repo")
        
        self.assertEqual(len(result), 5)
        self.assertIn("Command-line interface", result)
        self.assertIn("Graphical user interface", result)
        self.assertIn("Web interface", result)
        self.assertIn("Application programming interface", result)
        self.assertIn("Programmatic interface", result)

    @patch('src.modules.codemeta_input_method.detect_library_interface')
    @patch('src.modules.codemeta_input_method.detect_api_interface')
    @patch('src.modules.codemeta_input_method.detect_web_interface')
    @patch('src.modules.codemeta_input_method.detect_gui_interface')
    @patch('src.modules.codemeta_input_method.detect_cli_interface')
    def test_get_cli_only(self, mock_cli, mock_gui, mock_web, mock_api, mock_lib):
        """Test getting only CLI interface."""
        mock_cli.return_value = True
        mock_gui.return_value = False
        mock_web.return_value = False
        mock_api.return_value = False
        mock_lib.return_value = False
        
        result = codemeta_input_method.get_input_methods("owner", "repo")
        
        self.assertEqual(len(result), 1)
        self.assertIn("Command-line interface", result)

    @patch('src.modules.codemeta_input_method.detect_library_interface')
    @patch('src.modules.codemeta_input_method.detect_api_interface')
    @patch('src.modules.codemeta_input_method.detect_web_interface')
    @patch('src.modules.codemeta_input_method.detect_gui_interface')
    @patch('src.modules.codemeta_input_method.detect_cli_interface')
    def test_get_no_methods(self, mock_cli, mock_gui, mock_web, mock_api, mock_lib):
        """Test when no input methods are detected."""
        mock_cli.return_value = False
        mock_gui.return_value = False
        mock_web.return_value = False
        mock_api.return_value = False
        mock_lib.return_value = False
        
        result = codemeta_input_method.get_input_methods("owner", "repo")
        
        self.assertEqual(len(result), 0)


class TestMainInputMethodFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_input_method.get_input_methods')
    @patch('src.modules.codemeta_input_method.parse_repository_url')
    def test_get_input_methods(self, mock_parse, mock_get_methods):
        """Test get() function with input methods."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_methods.return_value = ["Command-line interface", "Web interface"]
        
        result = codemeta_input_method.get("https://github.com/owner/repo")
        
        self.assertIn("inputMethod", result)
        self.assertEqual(result["inputMethod"], ["Command-line interface", "Web interface"])

    @patch('src.modules.codemeta_input_method.get_input_methods')
    @patch('src.modules.codemeta_input_method.parse_repository_url')
    def test_get_no_input_methods(self, mock_parse, mock_get_methods):
        """Test get() function with no input methods."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_methods.return_value = []
        
        result = codemeta_input_method.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_input_method.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_input_method.get("invalid-url")
        
        self.assertEqual(result, {})


class TestInputMethodDataValidation(unittest.TestCase):
    """Test input method data validation."""

    @patch('src.modules.codemeta_input_method.get_input_methods')
    @patch('src.modules.codemeta_input_method.parse_repository_url')
    def test_input_method_is_list(self, mock_parse, mock_get_methods):
        """Test that inputMethod is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_methods.return_value = ["Command-line interface"]
        
        result = codemeta_input_method.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result.get("inputMethod"), list)

    @patch('src.modules.codemeta_input_method.get_input_methods')
    @patch('src.modules.codemeta_input_method.parse_repository_url')
    def test_input_method_items_are_strings(self, mock_parse, mock_get_methods):
        """Test that inputMethod items are strings."""
        mock_parse.return_value = ("owner", "repo")
        mock_get_methods.return_value = ["Command-line interface", "Web interface"]
        
        result = codemeta_input_method.get("https://github.com/owner/repo")
        
        for item in result.get("inputMethod", []):
            self.assertIsInstance(item, str)


if __name__ == '__main__':
    unittest.main()
