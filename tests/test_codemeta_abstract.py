"""
Unit tests for codemeta_abstract module
"""

import unittest
from src.modules.codemeta_abstract import AbstractExtractor, extract, get


class TestAbstractExtractor(unittest.TestCase):
    """Test cases for AbstractExtractor"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_repo_data = {
            "name": "test-repo",
            "owner": {"login": "test-owner"},
            "description": "",
            "language": "Python",
            "homepage": ""
        }

    def test_extract_simple_description(self):
        """Test extraction of simple repository description"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A simple test repository"

        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result, "A simple test repository")

    def test_extract_long_description(self):
        """Test extraction of long description (should be returned as-is if <= 1000 chars)"""
        repo_data = self.base_repo_data.copy()
        long_desc = "This is a comprehensive description of the project. " * 10
        repo_data["description"] = long_desc

        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(len(result) <= 1000)

    def test_extract_very_long_description(self):
        """Test extraction of very long description (should be truncated)"""
        repo_data = self.base_repo_data.copy()
        very_long_desc = "This is a very comprehensive description of the project. " * 50
        repo_data["description"] = very_long_desc

        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(len(result) <= 510)  # Truncated + "..."

    def test_extract_empty_description(self):
        """Test extraction with empty description"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = ""

        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_none_description(self):
        """Test extraction with None description"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = None

        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_whitespace_only_description(self):
        """Test extraction with whitespace-only description"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "   \n\t  "

        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_module_extract_function(self):
        """Test the module-level extract function"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Test abstract"

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "Test abstract")

    def test_module_extract_function_no_data(self):
        """Test extract function with no description"""
        repo_data = self.base_repo_data.copy()

        result = extract(repo_data)

        self.assertIsNone(result)

    def test_extract_flask_repository(self):
        """Test extraction from Flask repository"""
        repo_data = {
            "name": "flask",
            "owner": {"login": "pallets"},
            "description": "The Python micro framework for building web applications",
            "language": "Python",
            "homepage": "https://flask.palletsprojects.com/"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "The Python micro framework for building web applications")

    def test_extract_godot_repository(self):
        """Test extraction from Godot repository"""
        repo_data = {
            "name": "godot",
            "owner": {"login": "godotengine"},
            "description": "Godot Engine – Multi-platform 2D and 3D game engine",
            "language": "C++",
            "homepage": "https://godotengine.org"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "Godot Engine – Multi-platform 2D and 3D game engine")

    def test_extract_tensorflow_repository(self):
        """Test extraction from TensorFlow repository"""
        repo_data = {
            "name": "tensorflow",
            "owner": {"login": "tensorflow"},
            "description": "An Open Source Machine Learning Framework for Everyone",
            "language": "C++",
            "homepage": "https://www.tensorflow.org"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "An Open Source Machine Learning Framework for Everyone")


if __name__ == '__main__':
    unittest.main()
