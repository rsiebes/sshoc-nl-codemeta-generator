"""
Unit tests for codemeta_runtime_platform module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_runtime_platform


class TestRuntimePlatformExtraction(unittest.TestCase):
    """Test runtime platform extraction."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_basic_runtime_extraction(self, mock_fetch):
        """Test extraction of basic runtime platform information."""
        mock_fetch.return_value = "Requires Python 3.9 and Node.js 16"
        result = codemeta_runtime_platform.get("https://github.com/owner/repo")
        
        self.assertIn("runtimePlatform", result)
        self.assertIn("Node.js", result["runtimePlatform"])
        self.assertIn("Python", result["runtimePlatform"])

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_no_runtime_detected(self, mock_fetch):
        """Test handling of no runtime detected."""
        mock_fetch.return_value = None
        result = codemeta_runtime_platform.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_runtime_platform.get("invalid-url")
        
        self.assertEqual(result, {})


class TestPythonDetection(unittest.TestCase):
    """Test Python runtime detection."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_python_from_setup_py(self, mock_fetch):
        """Test detection of Python from setup.py."""
        setup = """
        python_requires='>=3.8',
        classifiers=[
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
        ]
        """
        mock_fetch.return_value = setup
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Python", result)

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_python_from_pyproject(self, mock_fetch):
        """Test detection of Python from pyproject.toml."""
        pyproject = """
        [project]
        requires-python = ">=3.8"
        """
        mock_fetch.side_effect = [None, None, pyproject, None, None, None, None, None, None]
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Python", result)


class TestNodeJsDetection(unittest.TestCase):
    """Test Node.js runtime detection."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_nodejs_from_package_json(self, mock_fetch):
        """Test detection of Node.js from package.json."""
        package_json = """
        {
            "name": "my-app",
            "engines": {
                "node": ">=16.0.0"
            }
        }
        """
        mock_fetch.return_value = package_json
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Node.js", result)


class TestJavaDetection(unittest.TestCase):
    """Test Java runtime detection."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_java_from_pom_xml(self, mock_fetch):
        """Test detection of Java from pom.xml."""
        pom_xml = """
        <project>
            <properties>
                <maven.compiler.source>11</maven.compiler.source>
                <maven.compiler.target>11</maven.compiler.target>
            </properties>
        </project>
        """
        # Mock returns: package.json, setup.py, pyproject.toml, requirements.txt, pom.xml (content)
        mock_fetch.side_effect = [None, None, None, None, pom_xml, None, None, None, None]
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Java", result)

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_java_from_gradle(self, mock_fetch):
        """Test detection of Java from build.gradle."""
        gradle = """
        sourceCompatibility = '11'
        targetCompatibility = '11'
        """
        # Mock returns: package.json, setup.py, pyproject.toml, requirements.txt, pom.xml, gradle (content), Gemfile, go.mod, Cargo.toml
        mock_fetch.side_effect = [None, None, None, None, None, gradle, None, None, None]
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Java", result)


class TestRubyDetection(unittest.TestCase):
    """Test Ruby runtime detection."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_ruby_from_gemfile(self, mock_fetch):
        """Test detection of Ruby from Gemfile."""
        gemfile = """
        ruby '3.0.0'
        """
        # Mock returns: all None until Gemfile
        mock_fetch.side_effect = [None, None, None, None, None, None, None, gemfile, None]
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Ruby", result)


class TestGoDetection(unittest.TestCase):
    """Test Go runtime detection."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_go_from_go_mod(self, mock_fetch):
        """Test detection of Go from go.mod."""
        go_mod = """
        go 1.18
        """
        # Mock returns: all None until go.mod
        mock_fetch.side_effect = [None, None, None, None, None, None, None, None, go_mod]
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Go", result)


class TestRustDetection(unittest.TestCase):
    """Test Rust runtime detection."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_detect_rust_from_cargo_toml(self, mock_fetch):
        """Test detection of Rust from Cargo.toml."""
        cargo_toml = """
        [package]
        name = "my-project"
        version = "0.1.0"
        """
        # Mock returns: package.json, setup.py, pyproject.toml, requirements.txt, pom.xml, gradle, Gemfile, go.mod, Cargo.toml (content)
        mock_fetch.side_effect = [None, None, None, None, None, None, None, None, cargo_toml]
        result = codemeta_runtime_platform.detect_from_package_files("owner", "repo")
        
        self.assertIn("Rust", result)


class TestRuntimeContent(unittest.TestCase):
    """Test runtime platform content validation."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_runtime_is_list(self, mock_fetch):
        """Test that runtime is a list."""
        mock_fetch.return_value = "Python 3.9"
        result = codemeta_runtime_platform.get("https://github.com/owner/repo")
        
        self.assertIn("runtimePlatform", result)
        self.assertIsInstance(result["runtimePlatform"], list)

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_runtime_not_empty(self, mock_fetch):
        """Test that runtime list is not empty."""
        mock_fetch.return_value = "Python 3.9"
        result = codemeta_runtime_platform.get("https://github.com/owner/repo")
        
        self.assertIn("runtimePlatform", result)
        self.assertTrue(len(result["runtimePlatform"]) > 0)

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_runtime_sorted(self, mock_fetch):
        """Test that runtime list is sorted."""
        mock_fetch.return_value = "Python 3.9 and Node.js 16"
        result = codemeta_runtime_platform.get("https://github.com/owner/repo")
        
        self.assertIn("runtimePlatform", result)
        self.assertEqual(result["runtimePlatform"], sorted(result["runtimePlatform"]))


class TestRealRepositories(unittest.TestCase):
    """Test runtime detection from real repositories."""

    @patch('src.modules.codemeta_runtime_platform.detect_from_package_files')
    @patch('src.modules.codemeta_runtime_platform.detect_from_readme')
    @patch('src.modules.codemeta_runtime_platform.detect_from_ci_config')
    def test_tensorflow_runtime(self, mock_ci, mock_readme, mock_package):
        """Test runtime detection from TensorFlow."""
        mock_package.return_value = ["Python 3.9"]
        mock_readme.return_value = ["Python"]
        mock_ci.return_value = ["Python"]
        
        result = codemeta_runtime_platform.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("runtimePlatform", result)
        self.assertIn("Python", result["runtimePlatform"])

    @patch('src.modules.codemeta_runtime_platform.detect_from_package_files')
    @patch('src.modules.codemeta_runtime_platform.detect_from_readme')
    @patch('src.modules.codemeta_runtime_platform.detect_from_ci_config')
    def test_flask_runtime(self, mock_ci, mock_readme, mock_package):
        """Test runtime detection from Flask."""
        mock_package.return_value = ["Python 3.8"]
        mock_readme.return_value = ["Python"]
        mock_ci.return_value = ["Python"]
        
        result = codemeta_runtime_platform.get("https://github.com/pallets/flask")
        
        self.assertIn("runtimePlatform", result)
        self.assertIn("Python", result["runtimePlatform"])

    @patch('src.modules.codemeta_runtime_platform.detect_from_package_files')
    @patch('src.modules.codemeta_runtime_platform.detect_from_readme')
    @patch('src.modules.codemeta_runtime_platform.detect_from_ci_config')
    def test_rust_runtime(self, mock_ci, mock_readme, mock_package):
        """Test runtime detection from Rust."""
        mock_package.return_value = ["Rust"]
        mock_readme.return_value = ["Rust"]
        mock_ci.return_value = []
        
        result = codemeta_runtime_platform.get("https://github.com/rust-lang/rust")
        
        self.assertIn("runtimePlatform", result)
        self.assertIn("Rust", result["runtimePlatform"])


class TestMultiplePlatforms(unittest.TestCase):
    """Test detection of multiple runtime platforms."""

    @patch('src.modules.codemeta_runtime_platform.fetch_file_content')
    def test_multiple_platforms(self, mock_fetch):
        """Test detection of multiple runtime platforms."""
        content = """
        Requires Python 3.9, Node.js 16, and Java 11
        """
        mock_fetch.return_value = content
        result = codemeta_runtime_platform.get("https://github.com/owner/repo")
        
        self.assertIn("runtimePlatform", result)
        self.assertGreater(len(result["runtimePlatform"]), 1)


if __name__ == '__main__':
    unittest.main()
