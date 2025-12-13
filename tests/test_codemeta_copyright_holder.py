import unittest
from src.modules.codemeta_copyright_holder import CopyrightHolderExtractor, extract

class TestCopyrightHolderExtractor(unittest.TestCase):
    def setUp(self):
        self.base_repo_data = {"owner": {"login": "test-user", "type": "User"}}

    def test_extract_user_owner(self):
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {"login": "john-doe", "type": "User", "name": "John Doe"}
        extractor = CopyrightHolderExtractor(repo_data)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertEqual(result, "John Doe")

    def test_extract_organization_owner(self):
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {"login": "mozilla", "type": "Organization", "name": "Mozilla Foundation"}
        extractor = CopyrightHolderExtractor(repo_data)
        result = extractor.extract()
        self.assertIsNotNone(result)
        self.assertEqual(result, "Mozilla Foundation")

    def test_module_extract_function(self):
        repo_data = self.base_repo_data.copy()
        result = extract(repo_data)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
