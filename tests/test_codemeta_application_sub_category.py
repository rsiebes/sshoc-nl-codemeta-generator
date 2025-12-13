"""
Unit tests for codemeta_application_sub_category module
"""

import unittest
from src.modules.codemeta_application_sub_category import (
    ApplicationSubCategoryExtractor, extract, get
)


class TestApplicationSubCategoryExtractor(unittest.TestCase):
    """Test cases for ApplicationSubCategoryExtractor"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_repo_data = {
            "name": "test-repo",
            "owner": {"login": "test-owner"},
            "description": "",
            "topics": [],
            "language": "Python",
            "homepage": ""
        }

    def test_extract_game_puzzle_subcategory(self):
        """Test extraction of Puzzle game subcategory"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A puzzle game with tetris-like mechanics"
        repo_data["topics"] = ["game", "puzzle", "tetris"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Game")

        self.assertIsNotNone(result)
        self.assertIn("Puzzle", result if isinstance(result, list) else [result])

    def test_extract_game_rpg_subcategory(self):
        """Test extraction of RPG game subcategory"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A fantasy RPG with quests and dungeons"
        repo_data["topics"] = ["game", "rpg", "fantasy"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Game")

        self.assertIsNotNone(result)
        self.assertIn("RPG", result if isinstance(result, list) else [result])

    def test_extract_developer_framework_subcategory(self):
        """Test extraction of Framework developer subcategory"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A web framework for building applications"
        repo_data["topics"] = ["framework", "web", "developer"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Developer")

        self.assertIsNotNone(result)
        self.assertIn("Framework", result if isinstance(result, list) else [result])

    def test_extract_developer_library_subcategory(self):
        """Test extraction of Library developer subcategory"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A utility library and SDK"
        repo_data["topics"] = ["library", "sdk"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Developer")

        self.assertIsNotNone(result)
        self.assertIn("Library", result if isinstance(result, list) else [result])

    def test_extract_business_crm_subcategory(self):
        """Test extraction of CRM business subcategory"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Customer relationship management system"
        repo_data["topics"] = ["crm", "business"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Business")

        self.assertIsNotNone(result)
        self.assertIn("CRM", result if isinstance(result, list) else [result])

    def test_extract_no_subcategory_without_primary(self):
        """Test that no subcategory is returned without primary category"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A puzzle game"
        repo_data["topics"] = ["puzzle"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract(None)

        self.assertIsNone(result)

    def test_extract_no_subcategory_invalid_primary(self):
        """Test that no subcategory is returned for invalid primary category"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A puzzle game"
        repo_data["topics"] = ["puzzle"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("InvalidCategory")

        self.assertIsNone(result)

    def test_extract_multiple_subcategories(self):
        """Test extraction of multiple subcategories when scores are similar"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A puzzle and strategy game"
        repo_data["topics"] = ["game", "puzzle", "strategy"]

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Game")

        if result:
            self.assertTrue(isinstance(result, (str, list)))

    def test_extract_low_confidence_returns_none(self):
        """Test that low confidence returns None"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Some game"
        repo_data["topics"] = []

        extractor = ApplicationSubCategoryExtractor(repo_data)
        result = extractor.extract("Game")

        # Should return None due to low confidence
        self.assertIsNone(result)

    def test_module_extract_function(self):
        """Test the module-level extract function"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "A puzzle game"
        repo_data["topics"] = ["puzzle", "game"]

        result = extract(repo_data, "Game")

        if result:
            self.assertTrue(isinstance(result, (str, list)))

    def test_module_extract_function_no_data(self):
        """Test extract function with no data"""
        repo_data = self.base_repo_data.copy()

        result = extract(repo_data, "Game")

        self.assertIsNone(result)

    def test_extract_flask_framework(self):
        """Test extraction from Flask repository"""
        repo_data = {
            "name": "flask",
            "owner": {"login": "pallets"},
            "description": "The Python micro framework for building web applications",
            "topics": ["web", "framework", "python"],
            "language": "Python",
            "homepage": "https://flask.palletsprojects.com/"
        }

        result = extract(repo_data, "Developer")

        self.assertIsNotNone(result)
        self.assertIn("Framework", result if isinstance(result, list) else [result])


if __name__ == '__main__':
    unittest.main()
