import unittest
from src.modules.codemeta_copyright_notice import CopyrightNoticeExtractor, extract

class TestCopyrightNoticeExtractor(unittest.TestCase):
    def setUp(self):
        self.base_repo_data = {"name": "test"}

    def test_extract_copyright_from_license(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {"LICENSE": "Copyright (c) 2021 Test Corp"}
        extractor = CopyrightNoticeExtractor(repo_data, repo_files)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertIn("Copyright", result)

    def test_extract_no_copyright_notice(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {}
        extractor = CopyrightNoticeExtractor(repo_data, repo_files)
        result = extractor.extract()
        self.assertIsNone(result)

    def test_module_extract_function(self):
        repo_data = self.base_repo_data.copy()
        repo_files = {"LICENSE": "Copyright (c) 2021"}
        result = extract(repo_data, repo_files)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
