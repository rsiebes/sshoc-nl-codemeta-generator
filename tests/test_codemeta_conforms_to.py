import unittest
from src.modules.codemeta_conforms_to import ConformsToExtractor, extract

class TestConformsToExtractor(unittest.TestCase):
    def setUp(self):
        self.base_repo_data = {"name": "test", "topics": [], "description": ""}

    def test_extract_rest_standard(self):
        repo_data = self.base_repo_data.copy()
        repo_data["topics"] = ["rest", "api"]
        extractor = ConformsToExtractor(repo_data)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertIn("fielding", result.lower() if isinstance(result, str) else str(result).lower())

    def test_extract_multiple_standards(self):
        repo_data = self.base_repo_data.copy()
        repo_data["topics"] = ["rest", "graphql"]
        extractor = ConformsToExtractor(repo_data)
        result = extractor.extract()
        self.assertIsNotNone(result)

    def test_extract_no_standards(self):
        repo_data = self.base_repo_data.copy()
        extractor = ConformsToExtractor(repo_data)
        result = extractor.extract()
        self.assertIsNone(result)

    def test_module_extract_function(self):
        repo_data = self.base_repo_data.copy()
        repo_data["topics"] = ["rest"]
        result = extract(repo_data)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
