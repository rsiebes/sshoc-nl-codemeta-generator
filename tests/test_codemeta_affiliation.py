"""
Unit tests for codemeta_affiliation module
"""

import unittest
from src.modules.codemeta_affiliation import AffiliationExtractor, extract, get


class TestAffiliationExtractor(unittest.TestCase):
    """Test cases for AffiliationExtractor"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_repo_data = {
            "name": "test-repo",
            "owner": {
                "login": "test-owner",
                "type": "User",
                "company": None
            },
            "organization": None,
            "description": "Test repository"
        }

    def test_extract_organization_owner(self):
        """Test extraction when owner is an organization"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "mozilla",
            "type": "Organization"
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result, "mozilla")

    def test_extract_user_with_company(self):
        """Test extraction when owner is a user with company affiliation"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User",
            "company": "Google"
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result, "Google")

    def test_extract_user_with_company_at_symbol(self):
        """Test extraction when company has @ symbol"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User",
            "company": "@Google"
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result, "Google")

    def test_extract_no_affiliation(self):
        """Test extraction with no affiliation data"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User",
            "company": None
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_empty_company_string(self):
        """Test extraction with empty company string"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User",
            "company": ""
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_whitespace_only_company(self):
        """Test extraction with whitespace-only company"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User",
            "company": "   \n\t  "
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_multiple_affiliations(self):
        """Test extraction with multiple affiliations"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "test-org",
            "type": "Organization"
        }
        repo_data["organization"] = {
            "login": "parent-org",
            "name": "Parent Organization"
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        if isinstance(result, list):
            self.assertIn("test-org", result)
            self.assertIn("parent-org", result)

    def test_extract_organization_field(self):
        """Test extraction from organization field"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User"
        }
        repo_data["organization"] = {
            "login": "mozilla",
            "name": "Mozilla Foundation"
        }

        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertEqual(result, "mozilla")

    def test_module_extract_function(self):
        """Test the module-level extract function"""
        repo_data = self.base_repo_data.copy()
        repo_data["owner"] = {
            "login": "john-doe",
            "type": "User",
            "company": "Google"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "Google")

    def test_module_extract_function_no_data(self):
        """Test extract function with no affiliation data"""
        repo_data = self.base_repo_data.copy()

        result = extract(repo_data)

        self.assertIsNone(result)

    def test_extract_pallets_flask(self):
        """Test extraction from Pallets/Flask repository"""
        repo_data = {
            "name": "flask",
            "owner": {
                "login": "pallets",
                "type": "Organization"
            },
            "organization": None,
            "description": "The Python micro framework for building web applications"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "pallets")

    def test_extract_tensorflow_organization(self):
        """Test extraction from TensorFlow organization"""
        repo_data = {
            "name": "tensorflow",
            "owner": {
                "login": "tensorflow",
                "type": "Organization"
            },
            "organization": None,
            "description": "An Open Source Machine Learning Framework"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "tensorflow")

    def test_extract_godot_organization(self):
        """Test extraction from Godot Engine organization"""
        repo_data = {
            "name": "godot",
            "owner": {
                "login": "godotengine",
                "type": "Organization"
            },
            "organization": None,
            "description": "Godot Engine – Multi-platform 2D and 3D game engine"
        }

        result = extract(repo_data)

        self.assertIsNotNone(result)
        self.assertEqual(result, "godotengine")


if __name__ == '__main__':
    unittest.main()
