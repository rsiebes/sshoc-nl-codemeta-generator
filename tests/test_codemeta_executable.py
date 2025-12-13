"""
Unit tests for the CodeMeta Executable Module
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_executable


class TestCLIEntryPointDetection(unittest.TestCase):
    """Test CLI entry point detection."""

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_setup_py_entry_points(self, mock_fetch):
        """Test detection of entry points from setup.py."""
        setup_py_content = """
        entry_points={
            'console_scripts': [
                'myapp=myapp.cli:main',
                'myapp-admin=myapp.admin:main',
            ],
        }
        """
        mock_fetch.side_effect = lambda owner, repo, path: setup_py_content if path == "setup.py" else None
        
        result = codemeta_executable.detect_cli_entry_points("owner", "repo")
        
        self.assertIn("myapp", result)
        self.assertIn("myapp-admin", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_pyproject_toml_scripts(self, mock_fetch):
        """Test detection of scripts from pyproject.toml."""
        pyproject_content = """
        [project.scripts]
        mycli = "mypackage.cli:main"
        myapp = "mypackage.app:run"
        """
        mock_fetch.side_effect = lambda owner, repo, path: pyproject_content if path == "pyproject.toml" else None
        
        result = codemeta_executable.detect_cli_entry_points("owner", "repo")
        
        self.assertIn("mycli", result)
        self.assertIn("myapp", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_poetry_scripts(self, mock_fetch):
        """Test detection of scripts from Poetry."""
        pyproject_content = """
        [tool.poetry.scripts]
        myapp = "myapp.cli:main"
        """
        mock_fetch.side_effect = lambda owner, repo, path: pyproject_content if path == "pyproject.toml" else None
        
        result = codemeta_executable.detect_cli_entry_points("owner", "repo")
        
        self.assertIn("myapp", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_package_json_bin(self, mock_fetch):
        """Test detection of bin field from package.json."""
        package_json_content = """
        {
            "name": "myapp",
            "bin": {
                "myapp": "./bin/cli.js",
                "myapp-admin": "./bin/admin.js"
            }
        }
        """
        mock_fetch.side_effect = lambda owner, repo, path: package_json_content if path == "package.json" else None
        
        result = codemeta_executable.detect_cli_entry_points("owner", "repo")
        
        self.assertIn("myapp", result)
        self.assertIn("myapp-admin", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_cargo_toml_bin(self, mock_fetch):
        """Test detection of binary targets from Cargo.toml."""
        cargo_toml_content = """
        [[bin]]
        name = "myapp"
        path = "src/main.rs"
        
        [[bin]]
        name = "myapp-cli"
        path = "src/cli.rs"
        """
        mock_fetch.side_effect = lambda owner, repo, path: cargo_toml_content if path == "Cargo.toml" else None
        
        result = codemeta_executable.detect_cli_entry_points("owner", "repo")
        
        self.assertIn("myapp", result)
        self.assertIn("myapp-cli", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_no_entry_points(self, mock_fetch):
        """Test when no entry points are found."""
        mock_fetch.return_value = None
        
        result = codemeta_executable.detect_cli_entry_points("owner", "repo")
        
        self.assertEqual(result, [])


class TestShellScriptDetection(unittest.TestCase):
    """Test shell script detection."""

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_bin_directory(self, mock_fetch):
        """Test detection of bin directory."""
        mock_fetch.side_effect = lambda owner, repo, path: "scripts" if path == "bin" else None
        
        result = codemeta_executable.detect_shell_scripts("owner", "repo")
        
        self.assertIn("bin/*", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_scripts_directory(self, mock_fetch):
        """Test detection of scripts directory."""
        mock_fetch.side_effect = lambda owner, repo, path: "scripts" if path == "scripts" else None
        
        result = codemeta_executable.detect_shell_scripts("owner", "repo")
        
        self.assertIn("scripts/*", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_detect_tools_directory(self, mock_fetch):
        """Test detection of tools directory."""
        mock_fetch.side_effect = lambda owner, repo, path: "tools" if path == "tools" else None
        
        result = codemeta_executable.detect_shell_scripts("owner", "repo")
        
        self.assertIn("tools/*", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    def test_no_shell_scripts(self, mock_fetch):
        """Test when no shell scripts are found."""
        mock_fetch.return_value = None
        
        result = codemeta_executable.detect_shell_scripts("owner", "repo")
        
        self.assertEqual(result, [])


class TestExecutableFileDetection(unittest.TestCase):
    """Test executable file detection."""

    @patch('src.modules.codemeta_executable.detect_shell_scripts')
    @patch('src.modules.codemeta_executable.detect_cli_entry_points')
    def test_detect_executable_files(self, mock_cli, mock_shell):
        """Test detection of executable files."""
        mock_cli.return_value = ["myapp", "myapp-admin"]
        mock_shell.return_value = ["bin/*"]
        
        result = codemeta_executable.detect_executable_files("owner", "repo")
        
        self.assertIn("myapp", result)
        self.assertIn("myapp-admin", result)
        self.assertIn("bin/*", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    @patch('src.modules.codemeta_executable.detect_shell_scripts')
    @patch('src.modules.codemeta_executable.detect_cli_entry_points')
    def test_detect_makefile_targets(self, mock_cli, mock_shell, mock_fetch):
        """Test detection of Makefile targets."""
        makefile_content = """all:
	@echo "Building..."

clean:
	rm -rf build/

test:
	pytest

run:
	python main.py

deploy:
	./deploy.sh
"""
        
        mock_cli.return_value = []
        mock_shell.return_value = []
        mock_fetch.side_effect = lambda owner, repo, path: makefile_content if path == "Makefile" else None
        
        result = codemeta_executable.detect_executable_files("owner", "repo")
        
        # Should include executable targets but exclude common non-executable ones
        self.assertIn("run", result)
        self.assertIn("deploy", result)

    @patch('src.modules.codemeta_executable.fetch_file_content')
    @patch('src.modules.codemeta_executable.detect_shell_scripts')
    @patch('src.modules.codemeta_executable.detect_cli_entry_points')
    def test_detect_python_executable_scripts(self, mock_cli, mock_shell, mock_fetch):
        """Test detection of Python executable scripts."""
        cli_py_content = "#!/usr/bin/env python\nif __name__ == '__main__':\n    main()"
        
        mock_cli.return_value = []
        mock_shell.return_value = []
        
        def fetch_side_effect(owner, repo, path):
            if path == "Makefile":
                return None
            elif path == "cli.py":
                return cli_py_content
            return None
        
        mock_fetch.side_effect = fetch_side_effect
        
        result = codemeta_executable.detect_executable_files("owner", "repo")
        
        self.assertIn("cli.py", result)

    @patch('src.modules.codemeta_executable.detect_shell_scripts')
    @patch('src.modules.codemeta_executable.detect_cli_entry_points')
    def test_no_executable_files(self, mock_cli, mock_shell):
        """Test when no executable files are found."""
        mock_cli.return_value = []
        mock_shell.return_value = []
        
        result = codemeta_executable.detect_executable_files("owner", "repo")
        
        self.assertEqual(result, [])


class TestExecutableInfoFormatting(unittest.TestCase):
    """Test executable info formatting."""

    def test_format_executable_info(self):
        """Test formatting of executable information."""
        executables = ["myapp", "myapp-admin", "cli"]
        
        result = codemeta_executable.format_executable_info(executables)
        
        self.assertIn("myapp", result)
        self.assertIn("myapp-admin", result)
        self.assertIn("cli", result)

    def test_format_executable_info_empty(self):
        """Test formatting with empty list."""
        result = codemeta_executable.format_executable_info([])
        
        self.assertIsNone(result)

    def test_format_executable_info_single(self):
        """Test formatting with single executable."""
        result = codemeta_executable.format_executable_info(["myapp"])
        
        self.assertEqual(result, "myapp")


class TestMainExecutableFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_executable.detect_executable_files')
    @patch('src.modules.codemeta_executable.parse_repository_url')
    def test_get_executable_info(self, mock_parse, mock_detect):
        """Test get() function with executable info."""
        mock_parse.return_value = ("owner", "repo")
        mock_detect.return_value = ["myapp", "myapp-admin"]
        
        result = codemeta_executable.get("https://github.com/owner/repo")
        
        self.assertIn("executable", result)
        self.assertEqual(result["executable"], ["myapp", "myapp-admin"])

    @patch('src.modules.codemeta_executable.detect_executable_files')
    @patch('src.modules.codemeta_executable.parse_repository_url')
    def test_get_no_executable_info(self, mock_parse, mock_detect):
        """Test get() function with no executable info."""
        mock_parse.return_value = ("owner", "repo")
        mock_detect.return_value = []
        
        result = codemeta_executable.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_executable.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_executable.get("invalid-url")
        
        self.assertEqual(result, {})


class TestExecutableDataValidation(unittest.TestCase):
    """Test executable data validation."""

    @patch('src.modules.codemeta_executable.detect_executable_files')
    @patch('src.modules.codemeta_executable.parse_repository_url')
    def test_executable_is_list(self, mock_parse, mock_detect):
        """Test that executable is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_detect.return_value = ["myapp", "myapp-admin"]
        
        result = codemeta_executable.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result.get("executable"), list)

    @patch('src.modules.codemeta_executable.detect_executable_files')
    @patch('src.modules.codemeta_executable.parse_repository_url')
    def test_executable_items_are_strings(self, mock_parse, mock_detect):
        """Test that executable items are strings."""
        mock_parse.return_value = ("owner", "repo")
        mock_detect.return_value = ["myapp", "myapp-admin"]
        
        result = codemeta_executable.get("https://github.com/owner/repo")
        
        for item in result.get("executable", []):
            self.assertIsInstance(item, str)


if __name__ == '__main__':
    unittest.main()
