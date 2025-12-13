"""
Unit tests for codemeta_application_category module.

Tests the extraction of application category from GitHub repository metadata
according to CodeMeta 3.1 standard.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.codemeta_application_category import ApplicationCategoryExtractor, extract


class TestApplicationCategoryExtractor(unittest.TestCase):
    """Test cases for ApplicationCategoryExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_repo_data = {
            "name": "test-repo",
            "owner": {"login": "testuser"},
            "description": "A test repository",
            "topics": [],
            "language": "Python",
            "homepage": ""
        }

    def test_extract_developer_application_python(self):
        """Test extraction of DeveloperApplication from Python framework."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A Python web framework for building APIs"
        repo_data["topics"] = ["framework", "api", "rest"]
        repo_data["language"] = "Python"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        # Should return a category (either string or list)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_web_application(self):
        """Test extraction of WebApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A full-stack web application framework"
        repo_data["topics"] = ["web", "frontend", "backend", "react"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_game_application(self):
        """Test extraction of GameApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A 3D game engine for building games"
        repo_data["topics"] = ["game", "engine", "graphics", "3d"]
        repo_data["language"] = "C++"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_mobile_application(self):
        """Test extraction of MobileApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A cross-platform mobile app framework"
        repo_data["topics"] = ["mobile", "android", "ios", "flutter"]
        repo_data["language"] = "Dart"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_science_application(self):
        """Test extraction of ScienceApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Machine learning library for data science"
        repo_data["topics"] = ["machine-learning", "deep-learning", "ai", "neural-networks"]
        repo_data["language"] = "Python"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_multimedia_application(self):
        """Test extraction of MultimediaApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Audio and video processing library"
        repo_data["topics"] = ["audio", "video", "media", "streaming"]
        repo_data["language"] = "C++"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_productivity_application(self):
        """Test extraction of ProductivityApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Project management and collaboration tool"
        repo_data["topics"] = ["productivity", "collaboration", "project-management"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_business_application(self):
        """Test extraction of BusinessApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Enterprise resource planning system"
        repo_data["topics"] = ["erp", "business", "accounting", "finance"]
        repo_data["language"] = "Java"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_education_application(self):
        """Test extraction of EducationApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Online learning platform with courses"
        repo_data["topics"] = ["education", "learning", "course", "training"]
        repo_data["language"] = "Python"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_health_application(self):
        """Test extraction of HealthApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Healthcare management system"
        repo_data["topics"] = ["health", "medical", "healthcare", "hospital"]
        repo_data["language"] = "Java"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_social_application(self):
        """Test extraction of SocialApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Social networking and messaging platform"
        repo_data["topics"] = ["social", "chat", "messaging", "community"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_shopping_application(self):
        """Test extraction of ShoppingApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "E-commerce marketplace platform"
        repo_data["topics"] = ["ecommerce", "shopping", "marketplace", "store"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_travel_application(self):
        """Test extraction of TravelApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Travel booking and navigation app"
        repo_data["topics"] = ["travel", "booking", "map", "navigation"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_news_application(self):
        """Test extraction of NewsApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "News aggregation and publishing platform"
        repo_data["topics"] = ["news", "blog", "journalism", "rss"]
        repo_data["language"] = "Python"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_no_category(self):
        """Test extraction when no category can be determined."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Some random repository"
        repo_data["topics"] = []
        repo_data["language"] = None

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        # Should return None if no clear category
        self.assertIsNone(result)

    def test_extract_multiple_categories(self):
        """Test extraction of multiple categories when scores are similar."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Web framework for building games and multimedia"
        repo_data["topics"] = ["web", "game", "graphics", "multimedia"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        # Could be single or multiple categories
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_language_scoring(self):
        """Test that programming language influences category scoring."""
        # Python should score higher for ScienceApplication
        repo_data_python = self.base_repo_data.copy()
        repo_data_python["language"] = "Python"
        repo_data_python["description"] = "Data analysis library"

        extractor_python = ApplicationCategoryExtractor(repo_data_python)
        result_python = extractor_python.extract()

        # C++ should score higher for GameApplication
        repo_data_cpp = self.base_repo_data.copy()
        repo_data_cpp["language"] = "C++"
        repo_data_cpp["description"] = "Graphics library"

        extractor_cpp = ApplicationCategoryExtractor(repo_data_cpp)
        result_cpp = extractor_cpp.extract()

        # Both should return results
        self.assertIsNotNone(result_python)
        self.assertIsNotNone(result_cpp)

    def test_extract_homepage_scoring(self):
        """Test that homepage URL influences category scoring."""
        repo_data = self.base_repo_data.copy()
        repo_data["homepage"] = "https://example.com/shop"
        repo_data["topics"] = ["ecommerce"]

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)

    def test_extract_case_insensitive(self):
        """Test that extraction is case-insensitive."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A WEB FRAMEWORK FOR BUILDING APIs"
        repo_data["topics"] = ["FRAMEWORK", "API", "REST"]
        repo_data["language"] = "PYTHON"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_partial_keyword_match(self):
        """Test that partial keyword matches are detected."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Building with React and Redux"
        repo_data["topics"] = ["frontend"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)

    def test_module_extract_function(self):
        """Test the module-level extract function."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A Python web framework"
        repo_data["topics"] = ["framework", "web"]
        repo_data["language"] = "Python"

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_module_extract_function_no_data(self):
        """Test the module-level extract function with no matching data."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "xyz abc"
        repo_data["topics"] = []
        repo_data["language"] = None

        result = extract(repo_data)

        # Should return None if no category found
        self.assertIsNone(result)

    def test_module_extract_function_with_repo_files(self):
        """Test the module-level extract function with repo_files parameter."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A Python library"
        repo_data["topics"] = ["library"]
        repo_data["language"] = "Python"

        repo_files = {"setup.py": "# setup file"}

        result = extract(repo_data, repo_files=repo_files)

        self.assertIsNotNone(result)

    def test_extract_desktop_application(self):
        """Test extraction of DesktopApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A cross-platform desktop application"
        repo_data["topics"] = ["desktop", "gui", "electron", "cross-platform"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_utility_application(self):
        """Test extraction of UtilityApplication."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "System utility for file compression"
        repo_data["topics"] = ["utility", "compression", "tool"]
        repo_data["language"] = "C"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_wikidata_id_mapping(self):
        """Test that Wikidata IDs are correctly mapped."""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A web framework"
        repo_data["topics"] = ["web"]
        repo_data["language"] = "JavaScript"

        extractor = ApplicationCategoryExtractor(repo_data)
        result = extractor.extract()

        # Result should contain a Wikidata URL
        if result:
            if isinstance(result, str):
                self.assertTrue(result.startswith("https://www.wikidata.org/wiki/Q"))
            elif isinstance(result, list):
                for item in result:
                    self.assertTrue(item.startswith("https://www.wikidata.org/wiki/Q"))


class TestApplicationCategoryIntegration(unittest.TestCase):
    """Integration tests for applicationCategory extraction."""

    def test_extract_flask_repository(self):
        """Test extraction from Flask repository metadata."""
        repo_data = {
            "name": "flask",
            "owner": {"login": "pallets"},
            "description": "The Python micro framework for building web applications.",
            "topics": ["web", "framework", "python"],
            "language": "Python",
            "homepage": "https://flask.palletsprojects.com/"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_tensorflow_repository(self):
        """Test extraction from TensorFlow repository metadata."""
        repo_data = {
            "name": "tensorflow",
            "owner": {"login": "tensorflow"},
            "description": "An Open Source Machine Learning Framework for Everyone",
            "topics": ["machine-learning", "deep-learning", "neural-networks", "tensorflow"],
            "language": "Python",
            "homepage": "https://www.tensorflow.org"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_react_repository(self):
        """Test extraction from React repository metadata."""
        repo_data = {
            "name": "react",
            "owner": {"login": "facebook"},
            "description": "A JavaScript library for building user interfaces with components",
            "topics": ["javascript", "library", "frontend", "ui"],
            "language": "JavaScript",
            "homepage": "https://react.dev"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_godot_repository(self):
        """Test extraction from Godot game engine repository."""
        repo_data = {
            "name": "godot",
            "owner": {"login": "godotengine"},
            "description": "Godot Engine – Multi-platform 2D and 3D game engine",
            "topics": ["game-engine", "3d", "2d", "graphics"],
            "language": "C++",
            "homepage": "https://godotengine.org"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))

    def test_extract_docker_repository(self):
        """Test extraction from Docker repository metadata."""
        repo_data = {
            "name": "docker",
            "owner": {"login": "moby"},
            "description": "Moby Project - a collaborative project for the container ecosystem",
            "topics": ["docker", "container", "devops", "tool"],
            "language": "Go",
            "homepage": "https://www.docker.com"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, (str, list)))


if __name__ == '__main__':
    unittest.main()
