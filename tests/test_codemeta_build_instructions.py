"""
Unit tests for the CodeMeta Build Instructions Module
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_build_instructions


class TestMakefileExtraction(unittest.TestCase):
    """Test build instruction extraction from Makefile."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_makefile(self, mock_fetch):
        """Test extraction from Makefile."""
        makefile_content = """
.PHONY: build install test

build:
	gcc -o myapp main.c

install:
	cp myapp /usr/local/bin/

test:
	./test.sh
        """
        mock_fetch.return_value = makefile_content
        
        result = codemeta_build_instructions.extract_from_makefile("owner", "repo")
        
        self.assertIsNotNone(result)
        self.assertIn("make", result)

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_makefile_no_file(self, mock_fetch):
        """Test when Makefile is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_makefile("owner", "repo")
        
        self.assertIsNone(result)


class TestSetupPyExtraction(unittest.TestCase):
    """Test build instruction extraction from setup.py."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_setup_py(self, mock_fetch):
        """Test extraction from setup.py."""
        setup_py_content = """
from setuptools import setup

setup(
    name='mypackage',
    version='1.0.0',
    py_modules=['mymodule']
)
        """
        mock_fetch.return_value = setup_py_content
        
        result = codemeta_build_instructions.extract_from_setup_py("owner", "repo")
        
        self.assertEqual(result, "python setup.py build")

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_setup_py_no_file(self, mock_fetch):
        """Test when setup.py is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_setup_py("owner", "repo")
        
        self.assertIsNone(result)


class TestPyprojectTomlExtraction(unittest.TestCase):
    """Test build instruction extraction from pyproject.toml."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_pyproject_poetry(self, mock_fetch):
        """Test extraction from pyproject.toml with Poetry."""
        pyproject_content = """
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "mypackage"
version = "1.0.0"
        """
        mock_fetch.return_value = pyproject_content
        
        result = codemeta_build_instructions.extract_from_pyproject_toml("owner", "repo")
        
        self.assertEqual(result, "poetry build")

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_pyproject_hatchling(self, mock_fetch):
        """Test extraction from pyproject.toml with Hatchling."""
        pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
        """
        mock_fetch.return_value = pyproject_content
        
        result = codemeta_build_instructions.extract_from_pyproject_toml("owner", "repo")
        
        self.assertEqual(result, "hatch build")

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_pyproject_no_file(self, mock_fetch):
        """Test when pyproject.toml is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_pyproject_toml("owner", "repo")
        
        self.assertIsNone(result)


class TestPackageJsonExtraction(unittest.TestCase):
    """Test build instruction extraction from package.json."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_package_json(self, mock_fetch):
        """Test extraction from package.json."""
        package_json_content = """
{
    "name": "mypackage",
    "version": "1.0.0",
    "scripts": {
        "build": "webpack --mode production",
        "test": "jest"
    }
}
        """
        mock_fetch.return_value = package_json_content
        
        result = codemeta_build_instructions.extract_from_package_json("owner", "repo")
        
        self.assertIsNotNone(result)
        self.assertIn("npm run build", result)

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_package_json_no_file(self, mock_fetch):
        """Test when package.json is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_package_json("owner", "repo")
        
        self.assertIsNone(result)


class TestCargoTomlExtraction(unittest.TestCase):
    """Test build instruction extraction from Cargo.toml."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_cargo_toml(self, mock_fetch):
        """Test extraction from Cargo.toml."""
        cargo_toml_content = """
[package]
name = "myapp"
version = "0.1.0"
edition = "2021"
        """
        mock_fetch.return_value = cargo_toml_content
        
        result = codemeta_build_instructions.extract_from_cargo_toml("owner", "repo")
        
        self.assertEqual(result, "cargo build --release")

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_cargo_toml_no_file(self, mock_fetch):
        """Test when Cargo.toml is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_cargo_toml("owner", "repo")
        
        self.assertIsNone(result)


class TestBuildGradleExtraction(unittest.TestCase):
    """Test build instruction extraction from build.gradle."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_build_gradle(self, mock_fetch):
        """Test extraction from build.gradle."""
        build_gradle_content = """
plugins {
    id 'java'
}

group = 'com.example'
version = '1.0.0'
        """
        mock_fetch.return_value = build_gradle_content
        
        result = codemeta_build_instructions.extract_from_build_gradle("owner", "repo")
        
        self.assertEqual(result, "./gradlew build")

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_build_gradle_no_file(self, mock_fetch):
        """Test when build.gradle is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_build_gradle("owner", "repo")
        
        self.assertIsNone(result)


class TestPomXmlExtraction(unittest.TestCase):
    """Test build instruction extraction from pom.xml."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_pom_xml(self, mock_fetch):
        """Test extraction from pom.xml."""
        pom_xml_content = """
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>myapp</artifactId>
    <version>1.0.0</version>
</project>
        """
        mock_fetch.return_value = pom_xml_content
        
        result = codemeta_build_instructions.extract_from_pom_xml("owner", "repo")
        
        self.assertEqual(result, "mvn clean install")

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_pom_xml_no_file(self, mock_fetch):
        """Test when pom.xml is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_pom_xml("owner", "repo")
        
        self.assertIsNone(result)


class TestReadmeExtraction(unittest.TestCase):
    """Test build instruction extraction from README.md."""

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_readme(self, mock_fetch):
        """Test extraction from README.md."""
        readme_content = """
# MyProject

## Build

To build the project:

```bash
make build
```

## Installation

```bash
make install
```
        """
        mock_fetch.return_value = readme_content
        
        result = codemeta_build_instructions.extract_from_readme("owner", "repo")
        
        self.assertIsNotNone(result)

    @patch('src.modules.codemeta_build_instructions.fetch_file_content')
    def test_extract_from_readme_no_file(self, mock_fetch):
        """Test when README.md is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_build_instructions.extract_from_readme("owner", "repo")
        
        self.assertIsNone(result)


class TestMainBuildInstructionsFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_build_instructions.extract_from_makefile')
    @patch('src.modules.codemeta_build_instructions.parse_repository_url')
    def test_get_build_instructions_from_makefile(self, mock_parse, mock_makefile):
        """Test get() function with Makefile."""
        mock_parse.return_value = ("owner", "repo")
        mock_makefile.return_value = "make build"
        
        result = codemeta_build_instructions.get("https://github.com/owner/repo")
        
        self.assertIn("buildInstructions", result)
        self.assertEqual(result["buildInstructions"], "make build")

    @patch('src.modules.codemeta_build_instructions.extract_from_setup_py')
    @patch('src.modules.codemeta_build_instructions.extract_from_makefile')
    @patch('src.modules.codemeta_build_instructions.parse_repository_url')
    def test_get_build_instructions_from_setup_py(self, mock_parse, mock_makefile, mock_setup):
        """Test get() function with setup.py."""
        mock_parse.return_value = ("owner", "repo")
        mock_makefile.return_value = None
        mock_setup.return_value = "python setup.py build"
        
        result = codemeta_build_instructions.get("https://github.com/owner/repo")
        
        self.assertIn("buildInstructions", result)
        self.assertEqual(result["buildInstructions"], "python setup.py build")

    @patch('src.modules.codemeta_build_instructions.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_build_instructions.get("invalid-url")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_build_instructions.extract_from_contributing')
    @patch('src.modules.codemeta_build_instructions.extract_from_readme')
    @patch('src.modules.codemeta_build_instructions.extract_from_pom_xml')
    @patch('src.modules.codemeta_build_instructions.extract_from_build_gradle')
    @patch('src.modules.codemeta_build_instructions.extract_from_cargo_toml')
    @patch('src.modules.codemeta_build_instructions.extract_from_package_json')
    @patch('src.modules.codemeta_build_instructions.extract_from_pyproject_toml')
    @patch('src.modules.codemeta_build_instructions.extract_from_setup_py')
    @patch('src.modules.codemeta_build_instructions.extract_from_makefile')
    @patch('src.modules.codemeta_build_instructions.parse_repository_url')
    def test_get_no_build_instructions(self, mock_parse, mock_makefile, mock_setup, mock_pyproject,
                                       mock_package, mock_cargo, mock_gradle, mock_pom, mock_readme, mock_contrib):
        """Test when no build instructions are found."""
        mock_parse.return_value = ("owner", "repo")
        mock_makefile.return_value = None
        mock_setup.return_value = None
        mock_pyproject.return_value = None
        mock_package.return_value = None
        mock_cargo.return_value = None
        mock_gradle.return_value = None
        mock_pom.return_value = None
        mock_readme.return_value = None
        mock_contrib.return_value = None
        
        result = codemeta_build_instructions.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})


class TestBuildInstructionsDataValidation(unittest.TestCase):
    """Test build instructions data validation."""

    @patch('src.modules.codemeta_build_instructions.extract_from_makefile')
    @patch('src.modules.codemeta_build_instructions.parse_repository_url')
    def test_build_instructions_is_string(self, mock_parse, mock_makefile):
        """Test that build instructions is a string."""
        mock_parse.return_value = ("owner", "repo")
        mock_makefile.return_value = "make build"
        
        result = codemeta_build_instructions.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result.get("buildInstructions"), str)

    @patch('src.modules.codemeta_build_instructions.extract_from_makefile')
    @patch('src.modules.codemeta_build_instructions.parse_repository_url')
    def test_build_instructions_not_empty(self, mock_parse, mock_makefile):
        """Test that build instructions is not empty."""
        mock_parse.return_value = ("owner", "repo")
        mock_makefile.return_value = "make build"
        
        result = codemeta_build_instructions.get("https://github.com/owner/repo")
        
        self.assertTrue(len(result.get("buildInstructions", "")) > 0)


if __name__ == '__main__':
    unittest.main()
