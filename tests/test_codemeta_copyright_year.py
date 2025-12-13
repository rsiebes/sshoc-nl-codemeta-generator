import unittest
from src.modules.codemeta_copyright_year import CopyrightYearExtractor, extract

class TestCopyrightYearExtractor(unittest.TestCase):
    def setUp(self):
        self.base_repo_data = {"created_at": "2014-05-10T00:00:00Z"}

    def test_extract_year_from_license(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {"LICENSE": "Copyright (c) 2021-2025 Test Corp"}
        extractor = CopyrightYearExtractor(repo_data, repo_files)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertIn("2021", result)

    def test_extract_year_from_created_at(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {}
        extractor = CopyrightYearExtractor(repo_data, repo_files)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertEqual(result, "2014")

    def test_module_extract_function(self):
        repo_data = self.base_repo_data.copy()
        result = extract(repo_data)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
