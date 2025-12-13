import unittest
from src.modules.codemeta_code_of_conduct import CodeOfConductExtractor, extract

class TestCodeOfConductExtractor(unittest.TestCase):
    def setUp(self):
        self.base_repo_data = {"name": "test", "html_url": "https://github.com/test/test"}

    def test_extract_code_of_conduct_md(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {"CODE_OF_CONDUCT.md": "# Code of Conduct"}
        extractor = CodeOfConductExtractor(repo_data, repo_files)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertIn("CODE_OF_CONDUCT.md", result)

    def test_extract_no_code_of_conduct(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {}
        extractor = CodeOfConductExtractor(repo_data, repo_files)
        result = extractor.extract()
        self.assertIsNone(result)

    def test_module_extract_function(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {"CODE_OF_CONDUCT.md": "# Code of Conduct"}
        result = extract(repo_data, repo_files)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
