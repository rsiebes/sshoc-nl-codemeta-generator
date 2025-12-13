"""
Unit tests for codemeta_aggregate_rating module
"""

import unittest
from src.modules.codemeta_aggregate_rating import AggregateRatingExtractor, extract, get


class TestAggregateRatingExtractor(unittest.TestCase):
    """Test cases for AggregateRatingExtractor"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_repo_data = {
            "name": "test-repo",
            "owner": {"login": "test-owner"},
            "stargazers_count": 0,
            "watchers_count": 0,
            "forks_count": 0,
            "description": "Test repository"
        }

    def test_extract_no_stars(self):
        """Test extraction with no stars"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 0

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_low_stars_rating_1(self):
        """Test extraction with 1-10 stars (rating 1)"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 5

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 1.0)
        self.assertEqual(result["ratingCount"], 5)

    def test_extract_medium_stars_rating_2(self):
        """Test extraction with 11-100 stars (rating 2)"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 50

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 2.0)
        self.assertEqual(result["ratingCount"], 50)

    def test_extract_good_stars_rating_3(self):
        """Test extraction with 101-500 stars (rating 3)"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 300

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 3.0)
        self.assertEqual(result["ratingCount"], 300)

    def test_extract_very_good_stars_rating_4(self):
        """Test extraction with 501-2000 stars (rating 4)"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 1000

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 4.0)
        self.assertEqual(result["ratingCount"], 1000)

    def test_extract_excellent_stars_rating_5(self):
        """Test extraction with 2000+ stars (rating 5)"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 5000

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 5.0)
        self.assertEqual(result["ratingCount"], 5000)

    def test_extract_rating_object_structure(self):
        """Test that rating object has correct structure"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 100

        extractor = AggregateRatingExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result["@type"], "AggregateRating")
        self.assertIn("ratingValue", result)
        self.assertIn("ratingCount", result)
        self.assertIn("bestRating", result)
        self.assertIn("worstRating", result)
        self.assertEqual(result["bestRating"], 5)
        self.assertEqual(result["worstRating"], 1)

    def test_module_extract_function(self):
        """Test the module-level extract function"""
        repo_data = self.base_repo_data.copy()
        repo_data["stargazers_count"] = 100

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 2.0)

    def test_module_extract_function_no_data(self):
        """Test extract function with no stars"""
        repo_data = self.base_repo_data.copy()

        result = extract(repo_data)

        self.assertIsNone(result)

    def test_extract_flask_repository(self):
        """Test extraction from Flask repository"""
        repo_data = {
            "name": "flask",
            "owner": {"login": "pallets"},
            "stargazers_count": 60000,
            "watchers_count": 2000,
            "forks_count": 15000,
            "description": "The Python micro framework for building web applications"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 5.0)
        self.assertEqual(result["ratingCount"], 60000)

    def test_extract_tensorflow_repository(self):
        """Test extraction from TensorFlow repository"""
        repo_data = {
            "name": "tensorflow",
            "owner": {"login": "tensorflow"},
            "stargazers_count": 180000,
            "watchers_count": 5000,
            "forks_count": 90000,
            "description": "An Open Source Machine Learning Framework"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 5.0)
        self.assertEqual(result["ratingCount"], 180000)

    def test_extract_godot_repository(self):
        """Test extraction from Godot repository"""
        repo_data = {
            "name": "godot",
            "owner": {"login": "godotengine"},
            "stargazers_count": 60000,
            "watchers_count": 2000,
            "forks_count": 10000,
            "description": "Godot Engine – Multi-platform 2D and 3D game engine"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result["ratingValue"], 5.0)
        self.assertEqual(result["ratingCount"], 60000)


if __name__ == '__main__':
    unittest.main()
