"""
Unit tests for the CodeMeta Documentation Module
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_documentation


class TestDocumentationPlatformDetection(unittest.TestCase):
    """Test documentation platform detection."""

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_sphinx(self, mock_fetch):
        """Test detection of Sphinx."""
        mock_fetch.side_effect = lambda owner, repo, path: "conf.py" if path == "docs/conf.py" else None
        
        result = codemeta_documentation.detect_documentation_platforms("owner", "repo")
        
        self.assertIn("Sphinx", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_mkdocs(self, mock_fetch):
        """Test detection of MkDocs."""
        mock_fetch.side_effect = lambda owner, repo, path: "mkdocs config" if path == "mkdocs.yml" else None
        
        result = codemeta_documentation.detect_documentation_platforms("owner", "repo")
        
        self.assertIn("MkDocs", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_doxygen(self, mock_fetch):
        """Test detection of Doxygen."""
        mock_fetch.side_effect = lambda owner, repo, path: "doxygen config" if path == "Doxyfile" else None
        
        result = codemeta_documentation.detect_documentation_platforms("owner", "repo")
        
        self.assertIn("Doxygen", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_jekyll(self, mock_fetch):
        """Test detection of Jekyll."""
        mock_fetch.side_effect = lambda owner, repo, path: "jekyll config" if path == "_config.yml" else None
        
        result = codemeta_documentation.detect_documentation_platforms("owner", "repo")
        
        self.assertIn("Jekyll", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_multiple_platforms(self, mock_fetch):
        """Test detection of multiple documentation platforms."""
        def side_effect(owner, repo, path):
            if path == "docs/conf.py":
                return "sphinx"
            elif path == "mkdocs.yml":
                return "mkdocs"
            elif path == "Doxyfile":
                return "doxygen"
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = codemeta_documentation.detect_documentation_platforms("owner", "repo")
        
        self.assertIn("Sphinx", result)
        self.assertIn("MkDocs", result)
        self.assertIn("Doxygen", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_no_documentation_platforms(self, mock_fetch):
        """Test when no documentation platforms are found."""
        mock_fetch.return_value = None
        
        result = codemeta_documentation.detect_documentation_platforms("owner", "repo")
        
        self.assertEqual(result, [])


class TestDocumentationFormatDetection(unittest.TestCase):
    """Test documentation format detection."""

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_markdown(self, mock_fetch):
        """Test detection of Markdown."""
        mock_fetch.side_effect = lambda owner, repo, path: "# README" if path == "README.md" else None
        
        result = codemeta_documentation.detect_documentation_formats("owner", "repo")
        
        self.assertIn("Markdown", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_restructuredtext(self, mock_fetch):
        """Test detection of reStructuredText."""
        mock_fetch.side_effect = lambda owner, repo, path: "conf.py" if path == "docs/conf.py" else None
        
        result = codemeta_documentation.detect_documentation_formats("owner", "repo")
        
        self.assertIn("reStructuredText", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_asciidoc(self, mock_fetch):
        """Test detection of AsciiDoc."""
        mock_fetch.side_effect = lambda owner, repo, path: "= Title" if path == "README.adoc" else None
        
        result = codemeta_documentation.detect_documentation_formats("owner", "repo")
        
        self.assertIn("AsciiDoc", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_orgmode(self, mock_fetch):
        """Test detection of Org-mode."""
        mock_fetch.side_effect = lambda owner, repo, path: "* Title" if path == "README.org" else None
        
        result = codemeta_documentation.detect_documentation_formats("owner", "repo")
        
        self.assertIn("Org-mode", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_multiple_formats(self, mock_fetch):
        """Test detection of multiple documentation formats."""
        def side_effect(owner, repo, path):
            if path == "README.md":
                return "# README"
            elif path == "docs/conf.py":
                return "conf"
            elif path == "README.adoc":
                return "= Title"
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = codemeta_documentation.detect_documentation_formats("owner", "repo")
        
        self.assertIn("Markdown", result)
        self.assertIn("reStructuredText", result)
        self.assertIn("AsciiDoc", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_no_documentation_formats(self, mock_fetch):
        """Test when no documentation formats are found."""
        mock_fetch.return_value = None
        
        result = codemeta_documentation.detect_documentation_formats("owner", "repo")
        
        self.assertEqual(result, [])


class TestDocumentationLocationDetection(unittest.TestCase):
    """Test documentation location detection."""

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_docs_directory(self, mock_fetch):
        """Test detection of docs directory."""
        mock_fetch.side_effect = lambda owner, repo, path: "docs" if path == "docs" else None
        
        result = codemeta_documentation.detect_documentation_locations("owner", "repo")
        
        self.assertIn("docs/", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_readme(self, mock_fetch):
        """Test detection of README."""
        mock_fetch.side_effect = lambda owner, repo, path: "# README" if path == "README.md" else None
        
        result = codemeta_documentation.detect_documentation_locations("owner", "repo")
        
        self.assertIn("README.md", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_contributing(self, mock_fetch):
        """Test detection of CONTRIBUTING."""
        mock_fetch.side_effect = lambda owner, repo, path: "Contributing" if path == "CONTRIBUTING.md" else None
        
        result = codemeta_documentation.detect_documentation_locations("owner", "repo")
        
        self.assertIn("CONTRIBUTING.md", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_changelog(self, mock_fetch):
        """Test detection of CHANGELOG."""
        mock_fetch.side_effect = lambda owner, repo, path: "Changelog" if path == "CHANGELOG.md" else None
        
        result = codemeta_documentation.detect_documentation_locations("owner", "repo")
        
        self.assertIn("CHANGELOG.md", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_multiple_locations(self, mock_fetch):
        """Test detection of multiple documentation locations."""
        def side_effect(owner, repo, path):
            if path == "docs":
                return "docs"
            elif path == "README.md":
                return "# README"
            elif path == "CONTRIBUTING.md":
                return "Contributing"
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = codemeta_documentation.detect_documentation_locations("owner", "repo")
        
        self.assertIn("docs/", result)
        self.assertIn("README.md", result)
        self.assertIn("CONTRIBUTING.md", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_no_documentation_locations(self, mock_fetch):
        """Test when no documentation locations are found."""
        mock_fetch.return_value = None
        
        result = codemeta_documentation.detect_documentation_locations("owner", "repo")
        
        self.assertEqual(result, [])


class TestExternalDocumentationDetection(unittest.TestCase):
    """Test external documentation platform detection."""

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_readthedocs(self, mock_fetch):
        """Test detection of ReadTheDocs."""
        mock_fetch.side_effect = lambda owner, repo, path: "rtd config" if path == ".readthedocs.yml" else None
        
        result = codemeta_documentation.detect_external_documentation("owner", "repo")
        
        self.assertIn("ReadTheDocs", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_netlify(self, mock_fetch):
        """Test detection of Netlify."""
        mock_fetch.side_effect = lambda owner, repo, path: "netlify config" if path == "netlify.toml" else None
        
        result = codemeta_documentation.detect_external_documentation("owner", "repo")
        
        self.assertIn("Netlify", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_detect_vercel(self, mock_fetch):
        """Test detection of Vercel."""
        mock_fetch.side_effect = lambda owner, repo, path: "vercel config" if path == "vercel.json" else None
        
        result = codemeta_documentation.detect_external_documentation("owner", "repo")
        
        self.assertIn("Vercel", result)

    @patch('src.modules.codemeta_documentation.fetch_file_content')
    def test_no_external_documentation(self, mock_fetch):
        """Test when no external documentation platforms are found."""
        mock_fetch.return_value = None
        
        result = codemeta_documentation.detect_external_documentation("owner", "repo")
        
        self.assertEqual(result, [])


class TestDocumentationInfoExtraction(unittest.TestCase):
    """Test documentation info extraction."""

    @patch('src.modules.codemeta_documentation.detect_external_documentation')
    @patch('src.modules.codemeta_documentation.detect_documentation_locations')
    @patch('src.modules.codemeta_documentation.detect_documentation_formats')
    @patch('src.modules.codemeta_documentation.detect_documentation_platforms')
    def test_extract_documentation_info(self, mock_platforms, mock_formats, mock_locations, mock_external):
        """Test extraction of documentation information."""
        mock_platforms.return_value = ["Sphinx"]
        mock_formats.return_value = ["reStructuredText"]
        mock_locations.return_value = ["docs/"]
        mock_external.return_value = ["ReadTheDocs"]
        
        result = codemeta_documentation.extract_documentation_info("owner", "repo")
        
        self.assertIn("platforms", result)
        self.assertIn("formats", result)
        self.assertIn("locations", result)
        self.assertIn("externalPlatforms", result)
        self.assertEqual(result["platforms"], ["Sphinx"])
        self.assertEqual(result["formats"], ["reStructuredText"])
        self.assertEqual(result["locations"], ["docs/"])
        self.assertEqual(result["externalPlatforms"], ["ReadTheDocs"])

    @patch('src.modules.codemeta_documentation.detect_external_documentation')
    @patch('src.modules.codemeta_documentation.detect_documentation_locations')
    @patch('src.modules.codemeta_documentation.detect_documentation_formats')
    @patch('src.modules.codemeta_documentation.detect_documentation_platforms')
    def test_extract_empty_documentation_info(self, mock_platforms, mock_formats, mock_locations, mock_external):
        """Test extraction when no documentation info found."""
        mock_platforms.return_value = []
        mock_formats.return_value = []
        mock_locations.return_value = []
        mock_external.return_value = []
        
        result = codemeta_documentation.extract_documentation_info("owner", "repo")
        
        self.assertEqual(result["platforms"], [])
        self.assertEqual(result["formats"], [])
        self.assertEqual(result["locations"], [])
        self.assertEqual(result["externalPlatforms"], [])


class TestDocumentationInfoFormatting(unittest.TestCase):
    """Test documentation info formatting."""

    def test_format_documentation_info_all_fields(self):
        """Test formatting with all fields."""
        doc_info = {
            "platforms": ["Sphinx", "MkDocs"],
            "formats": ["reStructuredText", "Markdown"],
            "locations": ["docs/", "README.md"],
            "externalPlatforms": ["ReadTheDocs", "Netlify"]
        }
        
        result = codemeta_documentation.format_documentation_info(doc_info)
        
        self.assertIn("Sphinx", result)
        self.assertIn("reStructuredText", result)
        self.assertIn("docs/", result)
        self.assertIn("ReadTheDocs", result)

    def test_format_documentation_info_partial_fields(self):
        """Test formatting with partial fields."""
        doc_info = {
            "platforms": ["Sphinx"],
            "formats": [],
            "locations": [],
            "externalPlatforms": []
        }
        
        result = codemeta_documentation.format_documentation_info(doc_info)
        
        self.assertIn("Sphinx", result)

    def test_format_documentation_info_empty(self):
        """Test formatting with empty fields."""
        doc_info = {
            "platforms": [],
            "formats": [],
            "locations": [],
            "externalPlatforms": []
        }
        
        result = codemeta_documentation.format_documentation_info(doc_info)
        
        self.assertIsNone(result)


class TestMainDocumentationFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_documentation.extract_documentation_info')
    @patch('src.modules.codemeta_documentation.parse_repository_url')
    def test_get_documentation_info(self, mock_parse, mock_extract):
        """Test get() function with documentation info."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": ["Sphinx"],
            "formats": ["reStructuredText"],
            "locations": ["docs/"],
            "externalPlatforms": ["ReadTheDocs"]
        }
        
        result = codemeta_documentation.get("https://github.com/owner/repo")
        
        self.assertIn("documentation", result)
        self.assertEqual(result["documentation"]["platforms"], ["Sphinx"])

    @patch('src.modules.codemeta_documentation.extract_documentation_info')
    @patch('src.modules.codemeta_documentation.parse_repository_url')
    def test_get_no_documentation_info(self, mock_parse, mock_extract):
        """Test get() function with no documentation info."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": [],
            "formats": [],
            "locations": [],
            "externalPlatforms": []
        }
        
        result = codemeta_documentation.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_documentation.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_documentation.get("invalid-url")
        
        self.assertEqual(result, {})


class TestDocumentationDataValidation(unittest.TestCase):
    """Test documentation data validation."""

    @patch('src.modules.codemeta_documentation.extract_documentation_info')
    @patch('src.modules.codemeta_documentation.parse_repository_url')
    def test_documentation_info_is_dict(self, mock_parse, mock_extract):
        """Test that documentation info is a dictionary."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": ["Sphinx"],
            "formats": ["reStructuredText"],
            "locations": ["docs/"],
            "externalPlatforms": []
        }
        
        result = codemeta_documentation.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result.get("documentation"), dict)

    @patch('src.modules.codemeta_documentation.extract_documentation_info')
    @patch('src.modules.codemeta_documentation.parse_repository_url')
    def test_documentation_platforms_is_list(self, mock_parse, mock_extract):
        """Test that platforms is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": ["Sphinx"],
            "formats": [],
            "locations": [],
            "externalPlatforms": []
        }
        
        result = codemeta_documentation.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result["documentation"]["platforms"], list)

    @patch('src.modules.codemeta_documentation.extract_documentation_info')
    @patch('src.modules.codemeta_documentation.parse_repository_url')
    def test_documentation_formats_is_list(self, mock_parse, mock_extract):
        """Test that formats is a list."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = {
            "platforms": [],
            "formats": ["Markdown", "reStructuredText"],
            "locations": [],
            "externalPlatforms": []
        }
        
        result = codemeta_documentation.get("https://github.com/owner/repo")
        
        self.assertIsInstance(result["documentation"]["formats"], list)


if __name__ == '__main__':
    unittest.main()
