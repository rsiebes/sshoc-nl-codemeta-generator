"""
Unit tests for codemeta_citation module
"""

import unittest
from src.modules.codemeta_citation import CitationExtractor, extract, get


class TestCitationExtractor(unittest.TestCase):
    """Test cases for CitationExtractor"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_repo_data = {
            "name": "test-repo",
            "owner": {"login": "test-owner"},
            "description": "Test repository"
        }

    def test_extract_no_citations(self):
        """Test extraction with no citation data"""
        repo_data = self.base_repo_data.copy()
        repo_files = {}

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_from_citation_cff(self):
        """Test extraction from CITATION.cff file"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "CITATION.cff": """cff-version: 1.2.0
message: "If you use this software, please cite it as below."
authors:
  - family-names: "Druskat"
    given-names: "Stephan"
title: "My Research Software"
version: 1.0.0
date-released: 2021-08-11
url: "https://github.com/citation-file-format/my-research-software"
"""
        }

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertIn("My Research Software", result)

    def test_extract_doi_from_readme(self):
        """Test extraction of DOI from README"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "README.md": """# My Project

Please cite this work using the following DOI: https://doi.org/10.5281/zenodo.1234567

## Usage
...
"""
        }

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertIn("https://doi.org/10.5281/zenodo.1234567", result)

    def test_extract_arxiv_from_readme(self):
        """Test extraction of arXiv reference from README"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "README.md": """# My Project

Related paper: arXiv:2101.12345

## Usage
...
"""
        }

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertIn("https://arxiv.org/abs/2101.12345", result)

    def test_extract_multiple_citations(self):
        """Test extraction of multiple citations"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "CITATION.cff": """title: "My Research Software"
""",
            "README.md": """# My Project

DOI: https://doi.org/10.5281/zenodo.1234567
arXiv: 2101.12345
"""
        }

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNotNone(result)
        if isinstance(result, list):
            self.assertGreaterEqual(len(result), 2)

    def test_extract_doi_from_description(self):
        """Test extraction of DOI from repository description"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Machine learning framework (DOI: 10.1234/example)"

        extractor = CitationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertIn("https://doi.org/10.1234/example", result)

    def test_extract_arxiv_from_description(self):
        """Test extraction of arXiv from repository description"""
        repo_data = self.base_repo_data.copy()
        repo_data["description"] = "Based on arXiv:2101.12345"

        extractor = CitationExtractor(repo_data)
        result = extractor.extract()

        self.assertIsNotNone(result)
        self.assertIn("https://arxiv.org/abs/2101.12345", result)

    def test_module_extract_function(self):
        """Test the module-level extract function"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "CITATION.cff": """title: "Test Software"
"""
        }

        result = extract(repo_data, repo_files)

        self.assertIsNotNone(result)
        self.assertIn("Test Software", result)

    def test_module_extract_function_no_data(self):
        """Test extract function with no citation data"""
        repo_data = self.base_repo_data.copy()

        result = extract(repo_data)

        self.assertIsNone(result)

    def test_extract_removes_duplicates(self):
        """Test that duplicate citations are removed"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "CITATION.cff": """title: "My Software"
""",
            "README.md": """# My Project

DOI: https://doi.org/10.5281/zenodo.1234567
"""
        }

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNotNone(result)
        # Should have at least 2 unique citations
        if isinstance(result, list):
            # Check no duplicates
            self.assertEqual(len(result), len(set(result)))

    def test_extract_empty_readme(self):
        """Test extraction with empty README"""
        repo_data = self.base_repo_data.copy()
        repo_files = {
            "README.md": ""
        }

        extractor = CitationExtractor(repo_data, repo_files)
        result = extractor.extract()

        self.assertIsNone(result)

    def test_extract_none_repo_files(self):
        """Test extraction with None repo_files"""
        repo_data = self.base_repo_data.copy()

        extractor = CitationExtractor(repo_data, None)
        result = extractor.extract()

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
