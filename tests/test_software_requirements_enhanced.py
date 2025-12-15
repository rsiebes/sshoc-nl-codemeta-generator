"""
Unit tests for enhanced SoftwareRequirementsMetadata module.

Tests the improved extraction capabilities including:
- Package manager file parsing (requirements.txt, package.json, etc.)
- README content extraction
- Language-based inference
- Version constraint validation
- Deduplication
"""

import unittest
from src.properties.software_requirements import SoftwareRequirementsMetadata


class TestSoftwareRequirementsEnhanced(unittest.TestCase):
    """Test cases for enhanced SoftwareRequirementsMetadata."""

    def test_extract_explicit_requirements(self):
        """Test extraction of explicit softwareRequirements field."""
        raw_data = {
            'software_requirements': ['Python >= 3.7', 'numpy >= 1.19.0']
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        self.assertEqual(len(result['softwareRequirements']), 2)
        self.assertIn('Python >= 3.7', result['softwareRequirements'])

    def test_parse_requirements_txt(self):
        """Test parsing of Python requirements.txt content."""
        requirements_content = """
# This is a comment
numpy>=1.19.0
scipy==1.5.4
pandas>=1.1.0  # inline comment
requests
"""
        raw_data = {
            'requirements_txt_content': requirements_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertIn('numpy>=1.19.0', reqs)
        self.assertIn('scipy==1.5.4', reqs)
        self.assertIn('pandas>=1.1.0', reqs)
        self.assertIn('requests', reqs)

    def test_parse_package_json(self):
        """Test parsing of Node.js package.json content."""
        package_json_content = """{
  "name": "my-app",
  "version": "1.0.0",
  "engines": {
    "node": ">=14.0.0"
  },
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "^4.17.21"
  }
}"""
        raw_data = {
            'package_json_content': package_json_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Node.js' in req for req in reqs))
        self.assertTrue(any('express' in req for req in reqs))

    def test_parse_gemfile(self):
        """Test parsing of Ruby Gemfile content."""
        gemfile_content = """
ruby '2.7.0'

gem 'rails', '~> 6.0'
gem 'pg', '~> 1.1'
gem 'puma', '~> 4.1'
"""
        raw_data = {
            'gemfile_content': gemfile_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Ruby' in req for req in reqs))
        self.assertTrue(any('rails' in req for req in reqs))

    def test_parse_cargo_toml(self):
        """Test parsing of Rust Cargo.toml content."""
        cargo_content = """
[package]
name = "my-app"
version = "0.1.0"
rust-version = "1.56"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
"""
        raw_data = {
            'cargo_toml_content': cargo_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Rust' in req for req in reqs))

    def test_extract_from_readme(self):
        """Test extraction of requirements from README content."""
        readme_content = """
# My Project

## Requirements

- Python >= 3.7
- numpy >= 1.19.0
- scipy >= 1.5.0

## Installation

```bash
pip install -r requirements.txt
```
"""
        raw_data = {
            'readme_content': readme_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Python' in req for req in reqs))

    def test_infer_from_language_python(self):
        """Test inference of requirements from Python language."""
        raw_data = {
            'languages': ['Python 85.5%', 'JavaScript 14.5%']
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Python' in req for req in reqs))

    def test_infer_from_language_nodejs(self):
        """Test inference of requirements from JavaScript language."""
        raw_data = {
            'languages': ['JavaScript 100.0%']
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Node.js' in req for req in reqs))

    def test_deduplicate_requirements(self):
        """Test deduplication of requirements."""
        raw_data = {
            'software_requirements': [
                'Python >= 3.7',
                'python >= 3.7',  # Duplicate (case-insensitive)
                'numpy >= 1.19.0'
            ]
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        # Should have 2 unique requirements
        python_count = sum(1 for r in reqs if 'python' in r.lower())
        self.assertEqual(python_count, 1)

    def test_validate_version_constraint_gte(self):
        """Test validation of >= version constraint."""
        metadata = SoftwareRequirementsMetadata({})
        self.assertTrue(metadata._is_valid_version_constraint('>= 3.7'))
        self.assertTrue(metadata._is_valid_version_constraint('>=3.7'))

    def test_validate_version_constraint_exact(self):
        """Test validation of == version constraint."""
        metadata = SoftwareRequirementsMetadata({})
        self.assertTrue(metadata._is_valid_version_constraint('== 1.5.4'))
        self.assertTrue(metadata._is_valid_version_constraint('==1.5.4'))

    def test_validate_version_constraint_semver(self):
        """Test validation of semantic version constraints."""
        metadata = SoftwareRequirementsMetadata({})
        self.assertTrue(metadata._is_valid_version_constraint('^4.17.1'))
        self.assertTrue(metadata._is_valid_version_constraint('~> 6.0'))

    def test_validate_version_constraint_simple(self):
        """Test validation of simple version numbers."""
        metadata = SoftwareRequirementsMetadata({})
        self.assertTrue(metadata._is_valid_version_constraint('1.5.4'))
        self.assertTrue(metadata._is_valid_version_constraint('3.7'))

    def test_validate_invalid_version_constraint(self):
        """Test validation rejects invalid version constraints."""
        metadata = SoftwareRequirementsMetadata({})
        self.assertFalse(metadata._is_valid_version_constraint('invalid'))
        self.assertFalse(metadata._is_valid_version_constraint(''))

    def test_validate_metadata_valid_list(self):
        """Test validation of valid requirement list."""
        raw_data = {
            'software_requirements': ['Python >= 3.7', 'numpy >= 1.19.0']
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()

        self.assertTrue(is_valid)
        self.assertEqual(len(metadata.get_errors()), 0)

    def test_validate_metadata_invalid_type(self):
        """Test validation fails for non-list requirements."""
        raw_data = {
            'software_requirements': 'Python >= 3.7'  # String instead of list
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        metadata.extract()
        is_valid = metadata.validate()

        # Should still work due to normalization
        self.assertTrue(is_valid)

    def test_validate_metadata_long_string(self):
        """Test validation warns for very long requirement strings."""
        long_req = 'Python >= 3.7 ' + 'x' * 200
        raw_data = {
            'software_requirements': [long_req]
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        metadata.extract()
        metadata.validate()

        warnings = metadata.get_warnings()
        self.assertTrue(any('too long' in w for w in warnings))

    def test_normalize_requirements_string(self):
        """Test normalization of string requirements."""
        metadata = SoftwareRequirementsMetadata({})
        result = metadata._normalize_requirements('Python >= 3.7')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'Python >= 3.7')

    def test_normalize_requirements_list(self):
        """Test normalization of list requirements."""
        metadata = SoftwareRequirementsMetadata({})
        result = metadata._normalize_requirements(['Python >= 3.7', 'numpy >= 1.19.0'])

        self.assertEqual(len(result), 2)

    def test_normalize_requirements_dict(self):
        """Test normalization of dict requirements."""
        metadata = SoftwareRequirementsMetadata({})
        req_dict = {'name': 'numpy', 'version': '>=1.19.0'}
        result = metadata._normalize_requirements(req_dict)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)

    def test_parse_setup_py(self):
        """Test parsing of Python setup.py file."""
        setup_content = """
from setuptools import setup

setup(
    name='my-package',
    version='1.0.0',
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
        'scipy>=1.5.0',
    ],
)
"""
        raw_data = {
            'setup_py_content': setup_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Python' in req for req in reqs))

    def test_parse_pyproject_toml(self):
        """Test parsing of Python pyproject.toml file."""
        pyproject_content = """
[project]
name = "my-package"
requires-python = ">=3.7"
dependencies = [
    "numpy>=1.19.0",
    "scipy>=1.5.0",
]
"""
        raw_data = {
            'pyproject_toml_content': pyproject_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Python' in req for req in reqs))

    def test_parse_pom_xml(self):
        """Test parsing of Java pom.xml file."""
        pom_content = """
<?xml version="1.0"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    <source>11</source>
    <dependencies>
        <dependency>
            <artifactId>junit</artifactId>
        </dependency>
    </dependencies>
</project>
"""
        raw_data = {
            'pom_xml_content': pom_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Java' in req for req in reqs))

    def test_parse_go_mod(self):
        """Test parsing of Go go.mod file."""
        go_mod_content = """
module github.com/example/myapp

go 1.16

require (
    github.com/gorilla/mux v1.8.0
    github.com/lib/pq v1.9.0
)
"""
        raw_data = {
            'go_mod_content': go_mod_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('Go' in req for req in reqs))

    def test_parse_composer_json(self):
        """Test parsing of PHP composer.json file."""
        composer_content = """{
    "name": "my-package",
    "require": {
        "php": ">=7.4",
        "laravel/framework": "^8.0"
    }
}"""
        raw_data = {
            'composer_json_content': composer_content
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertIn('softwareRequirements', result)
        reqs = result['softwareRequirements']
        self.assertTrue(any('PHP' in req for req in reqs))

    def test_empty_raw_data(self):
        """Test extraction with empty raw data."""
        raw_data = {}
        metadata = SoftwareRequirementsMetadata(raw_data)
        result = metadata.extract()

        self.assertEqual(result, {})
        warnings = metadata.get_warnings()
        self.assertTrue(any('could not be extracted' in w for w in warnings))

    def test_to_codemeta_dict(self):
        """Test conversion to Codemeta format."""
        raw_data = {
            'software_requirements': ['Python >= 3.7']
        }
        metadata = SoftwareRequirementsMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()

        self.assertIn('softwareRequirements', result)
        self.assertEqual(len(result['softwareRequirements']), 1)

    def test_to_codemeta_dict_empty(self):
        """Test conversion to Codemeta format with empty metadata."""
        raw_data = {}
        metadata = SoftwareRequirementsMetadata(raw_data)
        metadata.extract()
        result = metadata.to_codemeta_dict()

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
