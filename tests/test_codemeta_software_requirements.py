"""
Unit tests for codemeta_software_requirements module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_software_requirements


class TestSoftwareRequirementsExtraction(unittest.TestCase):
    """Test software requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_basic_requirements_extraction(self, mock_fetch):
        """Test extraction of basic software requirements."""
        mock_fetch.return_value = "requests==2.28.0\nnumpy>=1.20.0"
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertIn("softwareRequirements", result)
        self.assertTrue(len(result["softwareRequirements"]) > 0)

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_no_requirements_detected(self, mock_fetch):
        """Test handling of no requirements detected."""
        mock_fetch.return_value = None
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_software_requirements.get("invalid-url")
        
        self.assertEqual(result, {})


class TestPythonRequirements(unittest.TestCase):
    """Test Python requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_python_from_requirements_txt(self, mock_fetch):
        """Test extraction of Python requirements from requirements.txt."""
        requirements = """
requests==2.28.0
numpy>=1.20.0
pandas<2.0.0
# Comment line
scipy
"""
        mock_fetch.return_value = requirements
        result = codemeta_software_requirements.extract_python_requirements("owner", "repo")
        
        self.assertIn("Python package: requests", result)
        self.assertIn("Python package: numpy", result)
        self.assertIn("Python package: pandas", result)
        self.assertIn("Python package: scipy", result)

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_python_from_setup_py(self, mock_fetch):
        """Test extraction of Python requirements from setup.py."""
        setup_py = """
setup(
    install_requires=[
        'requests>=2.28.0',
        'numpy>=1.20.0',
    ]
)
"""
        mock_fetch.return_value = setup_py
        result = codemeta_software_requirements.extract_python_requirements("owner", "repo")
        
        self.assertIn("Python package: requests", result)
        self.assertIn("Python package: numpy", result)


class TestNodeJsRequirements(unittest.TestCase):
    """Test Node.js requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_nodejs_from_package_json(self, mock_fetch):
        """Test extraction of Node.js requirements from package.json."""
        package_json = """
{
    "dependencies": {
        "express": "^4.18.0",
        "react": "^18.0.0"
    },
    "devDependencies": {
        "webpack": "^5.0.0"
    }
}
"""
        mock_fetch.return_value = package_json
        result = codemeta_software_requirements.extract_nodejs_requirements("owner", "repo")
        
        self.assertIn("Node.js package: express", result)
        self.assertIn("Node.js package: react", result)
        self.assertIn("Node.js dev package: webpack", result)


class TestJavaRequirements(unittest.TestCase):
    """Test Java requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_java_from_pom_xml(self, mock_fetch):
        """Test extraction of Java requirements from pom.xml."""
        pom_xml = """
<project>
    <dependencies>
        <dependency>
            <artifactId>junit</artifactId>
        </dependency>
        <dependency>
            <artifactId>spring-core</artifactId>
        </dependency>
    </dependencies>
</project>
"""
        mock_fetch.return_value = pom_xml
        result = codemeta_software_requirements.extract_java_requirements("owner", "repo")
        
        self.assertIn("Java library: junit", result)
        self.assertIn("Java library: spring-core", result)


class TestRubyRequirements(unittest.TestCase):
    """Test Ruby requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_ruby_from_gemfile(self, mock_fetch):
        """Test extraction of Ruby requirements from Gemfile."""
        gemfile = """
source 'https://rubygems.org'

gem 'rails', '~> 7.0.0'
gem 'sqlite3'
gem 'puma'
"""
        mock_fetch.return_value = gemfile
        result = codemeta_software_requirements.extract_ruby_requirements("owner", "repo")
        
        self.assertIn("Ruby gem: rails", result)
        self.assertIn("Ruby gem: sqlite3", result)
        self.assertIn("Ruby gem: puma", result)


class TestGoRequirements(unittest.TestCase):
    """Test Go requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_go_from_go_mod(self, mock_fetch):
        """Test extraction of Go requirements from go.mod."""
        go_mod = """
module github.com/example/project

go 1.18

require (
    github.com/gorilla/mux v1.8.0
    github.com/lib/pq v1.10.0
)
"""
        mock_fetch.return_value = go_mod
        result = codemeta_software_requirements.extract_go_requirements("owner", "repo")
        
        self.assertIn("Go module: github.com/gorilla/mux", result)
        self.assertIn("Go module: github.com/lib/pq", result)


class TestRustRequirements(unittest.TestCase):
    """Test Rust requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_rust_from_cargo_toml(self, mock_fetch):
        """Test extraction of Rust requirements from Cargo.toml."""
        cargo_toml = """
[package]
name = "my-project"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
"""
        mock_fetch.return_value = cargo_toml
        result = codemeta_software_requirements.extract_rust_requirements("owner", "repo")
        
        self.assertIn("Rust crate: serde", result)
        self.assertIn("Rust crate: tokio", result)


class TestSystemRequirements(unittest.TestCase):
    """Test system requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_system_requirements(self, mock_fetch):
        """Test extraction of system requirements from README."""
        readme = """
# Installation

This project requires:
- PostgreSQL >= 12.0
- Redis >= 6.0
- Node.js version 16+

You need to install Docker before running the project.
"""
        mock_fetch.return_value = readme
        result = codemeta_software_requirements.extract_system_requirements("owner", "repo")
        
        self.assertTrue(len(result) > 0)


class TestRequirementsContent(unittest.TestCase):
    """Test requirements content validation."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_requirements_is_list(self, mock_fetch):
        """Test that requirements is a list."""
        mock_fetch.return_value = "requests==2.28.0"
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertIn("softwareRequirements", result)
        self.assertIsInstance(result["softwareRequirements"], list)

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_requirements_not_empty(self, mock_fetch):
        """Test that requirements list is not empty."""
        mock_fetch.return_value = "requests==2.28.0"
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertIn("softwareRequirements", result)
        self.assertTrue(len(result["softwareRequirements"]) > 0)

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_requirements_sorted(self, mock_fetch):
        """Test that requirements list is sorted."""
        mock_fetch.return_value = "requests==2.28.0\nnumpy>=1.20.0"
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertIn("softwareRequirements", result)
        self.assertEqual(result["softwareRequirements"], sorted(result["softwareRequirements"]))


class TestRealRepositories(unittest.TestCase):
    """Test requirements extraction from real repositories."""

    @patch('src.modules.codemeta_software_requirements.extract_python_requirements')
    @patch('src.modules.codemeta_software_requirements.extract_nodejs_requirements')
    @patch('src.modules.codemeta_software_requirements.extract_java_requirements')
    @patch('src.modules.codemeta_software_requirements.extract_ruby_requirements')
    @patch('src.modules.codemeta_software_requirements.extract_go_requirements')
    @patch('src.modules.codemeta_software_requirements.extract_rust_requirements')
    @patch('src.modules.codemeta_software_requirements.extract_system_requirements')
    def test_flask_requirements(self, mock_sys, mock_rust, mock_go, mock_ruby, mock_java, mock_nodejs, mock_python):
        """Test requirements extraction from Flask."""
        mock_python.return_value = ["Python package: Werkzeug", "Python package: Jinja2"]
        mock_nodejs.return_value = []
        mock_java.return_value = []
        mock_ruby.return_value = []
        mock_go.return_value = []
        mock_rust.return_value = []
        mock_sys.return_value = []
        
        result = codemeta_software_requirements.get("https://github.com/pallets/flask")
        
        self.assertIn("softwareRequirements", result)
        self.assertIn("Python package: Werkzeug", result["softwareRequirements"])


if __name__ == '__main__':
    unittest.main()
