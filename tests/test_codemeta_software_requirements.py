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


class TestVersionParsing(unittest.TestCase):
    """Test version specifier parsing."""

    def test_parse_exact_version(self):
        """Test parsing exact version specifier."""
        min_ver, max_ver = codemeta_software_requirements.parse_version_specifier("==1.0.0")
        self.assertEqual(min_ver, "1.0.0")
        self.assertEqual(max_ver, "1.0.0")

    def test_parse_greater_equal(self):
        """Test parsing >= version specifier."""
        min_ver, max_ver = codemeta_software_requirements.parse_version_specifier(">=1.0.0")
        self.assertEqual(min_ver, "1.0.0")
        self.assertIsNone(max_ver)

    def test_parse_less_equal(self):
        """Test parsing <= version specifier."""
        min_ver, max_ver = codemeta_software_requirements.parse_version_specifier("<=2.0.0")
        self.assertIsNone(min_ver)
        self.assertEqual(max_ver, "2.0.0")

    def test_parse_range(self):
        """Test parsing version range."""
        min_ver, max_ver = codemeta_software_requirements.parse_version_specifier("1.0.0-2.0.0")
        self.assertEqual(min_ver, "1.0.0")
        self.assertEqual(max_ver, "2.0.0")

    def test_parse_compatible_release(self):
        """Test parsing compatible release specifier."""
        min_ver, max_ver = codemeta_software_requirements.parse_version_specifier("~=1.4.5")
        self.assertEqual(min_ver, "1.4.5")
        self.assertEqual(max_ver, "1.5")


class TestSoftwareApplicationCreation(unittest.TestCase):
    """Test SoftwareApplication object creation."""

    def test_create_requirement_without_version(self):
        """Test creating requirement without version."""
        req = codemeta_software_requirements.create_software_requirement("requests")
        
        self.assertEqual(req["@type"], "SoftwareApplication")
        self.assertEqual(req["name"], "requests")
        self.assertNotIn("minVersion", req)
        self.assertNotIn("maxVersion", req)

    def test_create_requirement_with_version(self):
        """Test creating requirement with version."""
        req = codemeta_software_requirements.create_software_requirement("requests", ">=2.28.0")
        
        self.assertEqual(req["@type"], "SoftwareApplication")
        self.assertEqual(req["name"], "requests")
        self.assertEqual(req["minVersion"], "2.28.0")
        self.assertNotIn("maxVersion", req)

    def test_create_requirement_with_range(self):
        """Test creating requirement with version range."""
        req = codemeta_software_requirements.create_software_requirement("flask", "1.0.0-2.0.0")
        
        self.assertEqual(req["@type"], "SoftwareApplication")
        self.assertEqual(req["name"], "flask")
        self.assertEqual(req["minVersion"], "1.0.0")
        self.assertEqual(req["maxVersion"], "2.0.0")


class TestPythonRequirements(unittest.TestCase):
    """Test Python requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_python_from_requirements_txt(self, mock_fetch):
        """Test extraction of Python requirements from requirements.txt."""
        requirements = """
requests==2.28.0
numpy>=1.20.0
pandas<2.0.0
scipy
"""
        mock_fetch.return_value = requirements
        result = codemeta_software_requirements.extract_python_requirements("owner", "repo")
        
        self.assertTrue(any(r['name'] == 'requests' for r in result))
        self.assertTrue(any(r['name'] == 'numpy' for r in result))
        self.assertTrue(any(r['name'] == 'pandas' for r in result))
        self.assertTrue(any(r['name'] == 'scipy' for r in result))
        
        # Check version extraction
        requests_req = next(r for r in result if r['name'] == 'requests')
        self.assertEqual(requests_req.get('minVersion'), '2.28.0')
        self.assertEqual(requests_req.get('maxVersion'), '2.28.0')


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
    }
}
"""
        mock_fetch.return_value = package_json
        result = codemeta_software_requirements.extract_nodejs_requirements("owner", "repo")
        
        self.assertTrue(any(r['name'] == 'express' for r in result))
        self.assertTrue(any(r['name'] == 'react' for r in result))


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
            <version>4.13.2</version>
        </dependency>
    </dependencies>
</project>
"""
        mock_fetch.return_value = pom_xml
        result = codemeta_software_requirements.extract_java_requirements("owner", "repo")
        
        self.assertTrue(any(r['name'] == 'junit' for r in result))
        junit_req = next(r for r in result if r['name'] == 'junit')
        self.assertEqual(junit_req.get('minVersion'), '4.13.2')


class TestRubyRequirements(unittest.TestCase):
    """Test Ruby requirements extraction."""

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_extract_ruby_from_gemfile(self, mock_fetch):
        """Test extraction of Ruby requirements from Gemfile."""
        gemfile = """
source 'https://rubygems.org'

gem 'rails', '~> 7.0.0'
gem 'sqlite3'
"""
        mock_fetch.return_value = gemfile
        result = codemeta_software_requirements.extract_ruby_requirements("owner", "repo")
        
        self.assertTrue(any(r['name'] == 'rails' for r in result))
        self.assertTrue(any(r['name'] == 'sqlite3' for r in result))


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
        
        self.assertTrue(any(r['name'] == 'github.com/gorilla/mux' for r in result))
        self.assertTrue(any(r['name'] == 'github.com/lib/pq' for r in result))


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
tokio = "1.0"
"""
        mock_fetch.return_value = cargo_toml
        result = codemeta_software_requirements.extract_rust_requirements("owner", "repo")
        
        self.assertTrue(any(r['name'] == 'serde' for r in result))
        self.assertTrue(any(r['name'] == 'tokio' for r in result))


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
    def test_requirements_are_software_applications(self, mock_fetch):
        """Test that requirements are SoftwareApplication objects."""
        mock_fetch.return_value = "requests==2.28.0"
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertIn("softwareRequirements", result)
        for req in result["softwareRequirements"]:
            self.assertEqual(req.get("@type"), "SoftwareApplication")
            self.assertIn("name", req)

    @patch('src.modules.codemeta_software_requirements.fetch_file_content')
    def test_requirements_sorted(self, mock_fetch):
        """Test that requirements list is sorted."""
        mock_fetch.return_value = "requests==2.28.0\nnumpy>=1.20.0"
        result = codemeta_software_requirements.get("https://github.com/owner/repo")
        
        self.assertIn("softwareRequirements", result)
        names = [r.get('name') for r in result["softwareRequirements"]]
        self.assertEqual(names, sorted(names))


if __name__ == '__main__':
    unittest.main()
