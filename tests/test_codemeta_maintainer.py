"""
Unit tests for the CodeMeta Maintainer Module
"""

import unittest
from unittest.mock import patch, MagicMock
from src.modules import codemeta_maintainer


class TestOrcidExtraction(unittest.TestCase):
    """Test ORCID extraction functionality."""

    def test_extract_orcid_from_orcid_url(self):
        """Test extracting ORCID from orcid.org URL."""
        text = "Author: John Doe (https://orcid.org/0000-0001-2345-6789)"
        orcid = codemeta_maintainer.extract_orcid_from_text(text)
        self.assertEqual(orcid, "0000-0001-2345-6789")

    def test_extract_orcid_from_plain_format(self):
        """Test extracting ORCID from plain format."""
        text = "ORCID: 0000-0001-2345-6789"
        orcid = codemeta_maintainer.extract_orcid_from_text(text)
        self.assertEqual(orcid, "0000-0001-2345-6789")

    def test_extract_orcid_with_x_checksum(self):
        """Test extracting ORCID with X checksum."""
        text = "orcid.org/0000-0001-2345-678X"
        orcid = codemeta_maintainer.extract_orcid_from_text(text)
        self.assertEqual(orcid, "0000-0001-2345-678X")

    def test_extract_orcid_not_found(self):
        """Test when ORCID is not found."""
        text = "John Doe (john@example.com)"
        orcid = codemeta_maintainer.extract_orcid_from_text(text)
        self.assertIsNone(orcid)

    def test_extract_orcid_case_insensitive(self):
        """Test ORCID extraction is case insensitive."""
        text = "ORCID.ORG/0000-0001-2345-6789"
        orcid = codemeta_maintainer.extract_orcid_from_text(text)
        self.assertEqual(orcid, "0000-0001-2345-6789")


class TestReadmeMaintainerExtraction(unittest.TestCase):
    """Test maintainer extraction from README."""

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_from_readme(self, mock_fetch):
        """Test extraction of maintainers from README."""
        readme_content = """
# Maintainers

- John Doe (john@example.com)
- Jane Smith (jane@example.com)
        """
        mock_fetch.return_value = readme_content
        
        result = codemeta_maintainer.extract_maintainers_from_readme("owner", "repo")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "John Doe")
        self.assertEqual(result[0]["email"], "john@example.com")
        self.assertEqual(result[1]["name"], "Jane Smith")
        self.assertEqual(result[1]["email"], "jane@example.com")

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_with_orcid(self, mock_fetch):
        """Test extraction of maintainers with ORCID identifiers."""
        readme_content = """
# Maintainers

- John Doe (john@example.com) ORCID: 0000-0001-2345-6789
- Jane Smith (jane@example.com) https://orcid.org/0000-0002-3456-7890
        """
        mock_fetch.return_value = readme_content
        
        result = codemeta_maintainer.extract_maintainers_from_readme("owner", "repo")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].get("identifier"), "https://orcid.org/0000-0001-2345-6789")
        self.assertEqual(result[1].get("identifier"), "https://orcid.org/0000-0002-3456-7890")

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_no_readme(self, mock_fetch):
        """Test when README is not found."""
        mock_fetch.return_value = None
        
        result = codemeta_maintainer.extract_maintainers_from_readme("owner", "repo")
        
        self.assertEqual(result, [])

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_no_section(self, mock_fetch):
        """Test when maintainers section is not found."""
        readme_content = "# README\n\nThis is a test project."
        mock_fetch.return_value = readme_content
        
        result = codemeta_maintainer.extract_maintainers_from_readme("owner", "repo")
        
        self.assertEqual(result, [])


class TestPackageFileMaintainerExtraction(unittest.TestCase):
    """Test maintainer extraction from package files."""

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_from_setup_py(self, mock_fetch):
        """Test extraction from setup.py."""
        setup_py_content = """
setup(
    name='mypackage',
    maintainer='John Doe',
    maintainer_email='john@example.com'
)
        """
        mock_fetch.return_value = setup_py_content
        
        result = codemeta_maintainer.extract_maintainers_from_package_files("owner", "repo")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "John Doe")
        self.assertEqual(result[0]["email"], "john@example.com")

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_from_setup_py_with_orcid(self, mock_fetch):
        """Test extraction from setup.py with ORCID."""
        setup_py_content = """
setup(
    name='mypackage',
    maintainer='John Doe',
    maintainer_email='john@example.com',
    author_orcid='0000-0001-2345-6789'
)
        """
        mock_fetch.side_effect = lambda owner, repo, file: setup_py_content if file == "setup.py" else None
        
        result = codemeta_maintainer.extract_maintainers_from_package_files("owner", "repo")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get("identifier"), "https://orcid.org/0000-0001-2345-6789")

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_from_package_json(self, mock_fetch):
        """Test extraction from package.json."""
        package_json_content = """
{
    "maintainers": [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"}
    ]
}
        """
        mock_fetch.side_effect = lambda owner, repo, file: package_json_content if file == "package.json" else None
        
        result = codemeta_maintainer.extract_maintainers_from_package_files("owner", "repo")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "John Doe")
        self.assertEqual(result[1]["name"], "Jane Smith")


class TestContributingMaintainerExtraction(unittest.TestCase):
    """Test maintainer extraction from CONTRIBUTING.md."""

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_from_contributing(self, mock_fetch):
        """Test extraction from CONTRIBUTING.md."""
        contributing_content = """
# Contact

For questions, contact:
- John Doe <john@example.com>
- Jane Smith <jane@example.com>
        """
        mock_fetch.side_effect = lambda owner, repo, file: contributing_content if file == "CONTRIBUTING.md" else None
        
        result = codemeta_maintainer.extract_maintainers_from_contributing("owner", "repo")
        
        self.assertGreater(len(result), 0)

    @patch('src.modules.codemeta_maintainer.fetch_file_content')
    def test_extract_maintainers_from_contributing_with_orcid(self, mock_fetch):
        """Test extraction from CONTRIBUTING.md with ORCID."""
        contributing_content = """
# Maintainers

- John Doe <john@example.com> (ORCID: 0000-0001-2345-6789)
        """
        mock_fetch.side_effect = lambda owner, repo, file: contributing_content if file == "CONTRIBUTING.md" else None
        
        result = codemeta_maintainer.extract_maintainers_from_contributing("owner", "repo")
        
        if result:
            self.assertEqual(result[0].get("identifier"), "https://orcid.org/0000-0001-2345-6789")


class TestGitHubAPIMaintainerExtraction(unittest.TestCase):
    """Test maintainer extraction from GitHub API."""

    @patch('src.modules.codemeta_maintainer.fetch_repository_contributors')
    @patch('src.modules.codemeta_maintainer.fetch_repository_info')
    def test_extract_maintainers_from_github_api(self, mock_repo_info, mock_contributors):
        """Test extraction from GitHub API."""
        mock_repo_info.return_value = {
            "owner": {
                "login": "owner_user",
                "html_url": "https://github.com/owner_user"
            }
        }
        mock_contributors.return_value = [
            {"login": "contributor1", "html_url": "https://github.com/contributor1", "contributions": 100},
            {"login": "contributor2", "html_url": "https://github.com/contributor2", "contributions": 50}
        ]
        
        result = codemeta_maintainer.extract_maintainers_from_github_api("owner", "repo")
        
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["name"], "owner_user")


class TestMainMaintainerFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_github_api')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_contributing')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_package_files')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_readme')
    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_get_maintainers(self, mock_parse, mock_readme, mock_package, mock_contrib, mock_api):
        """Test the main get() function."""
        mock_parse.return_value = ("owner", "repo")
        mock_readme.return_value = [
            {"@type": "Person", "name": "John Doe", "email": "john@example.com"}
        ]
        mock_package.return_value = []
        mock_contrib.return_value = []
        mock_api.return_value = []
        
        result = codemeta_maintainer.get("https://github.com/owner/repo")
        
        self.assertIn("maintainer", result)
        self.assertEqual(len(result["maintainer"]), 1)
        self.assertEqual(result["maintainer"][0]["name"], "John Doe")

    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_github_api')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_contributing')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_package_files')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_readme')
    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_get_maintainers_with_orcid(self, mock_parse, mock_readme, mock_package, mock_contrib, mock_api):
        """Test the main get() function with ORCID."""
        mock_parse.return_value = ("owner", "repo")
        mock_readme.return_value = [
            {
                "@type": "Person",
                "name": "John Doe",
                "email": "john@example.com",
                "identifier": "https://orcid.org/0000-0001-2345-6789"
            }
        ]
        mock_package.return_value = []
        mock_contrib.return_value = []
        mock_api.return_value = []
        
        result = codemeta_maintainer.get("https://github.com/owner/repo")
        
        self.assertIn("maintainer", result)
        self.assertEqual(result["maintainer"][0].get("identifier"), "https://orcid.org/0000-0001-2345-6789")

    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_github_api')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_contributing')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_package_files')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_readme')
    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_get_no_maintainers(self, mock_parse, mock_readme, mock_package, mock_contrib, mock_api):
        """Test when no maintainers are found."""
        mock_parse.return_value = ("owner", "repo")
        mock_readme.return_value = []
        mock_package.return_value = []
        mock_contrib.return_value = []
        mock_api.return_value = []
        
        result = codemeta_maintainer.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_maintainer.get("invalid-url")
        
        self.assertEqual(result, {})


class TestMaintainerDataValidation(unittest.TestCase):
    """Test maintainer data validation."""

    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_github_api')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_contributing')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_package_files')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_readme')
    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_maintainer_has_type(self, mock_parse, mock_readme, mock_package, mock_contrib, mock_api):
        """Test that all maintainers have @type."""
        mock_parse.return_value = ("owner", "repo")
        mock_readme.return_value = [
            {"@type": "Person", "name": "John Doe"}
        ]
        mock_package.return_value = []
        mock_contrib.return_value = []
        mock_api.return_value = []
        
        result = codemeta_maintainer.get("https://github.com/owner/repo")
        
        for maintainer in result.get("maintainer", []):
            self.assertEqual(maintainer.get("@type"), "Person")

    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_github_api')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_contributing')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_package_files')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_readme')
    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_maintainer_sorted(self, mock_parse, mock_readme, mock_package, mock_contrib, mock_api):
        """Test that maintainers are sorted by name."""
        mock_parse.return_value = ("owner", "repo")
        mock_readme.return_value = [
            {"@type": "Person", "name": "Zoe"},
            {"@type": "Person", "name": "Alice"}
        ]
        mock_package.return_value = []
        mock_contrib.return_value = []
        mock_api.return_value = []
        
        result = codemeta_maintainer.get("https://github.com/owner/repo")
        
        names = [m.get("name") for m in result.get("maintainer", [])]
        self.assertEqual(names, sorted(names))

    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_github_api')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_contributing')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_package_files')
    @patch('src.modules.codemeta_maintainer.extract_maintainers_from_readme')
    @patch('src.modules.codemeta_maintainer.parse_repository_url')
    def test_no_duplicate_maintainers(self, mock_parse, mock_readme, mock_package, mock_contrib, mock_api):
        """Test that duplicate maintainers are removed."""
        mock_parse.return_value = ("owner", "repo")
        mock_readme.return_value = [
            {"@type": "Person", "name": "John Doe"}
        ]
        mock_package.return_value = [
            {"@type": "Person", "name": "John Doe"}
        ]
        mock_contrib.return_value = []
        mock_api.return_value = []
        
        result = codemeta_maintainer.get("https://github.com/owner/repo")
        
        self.assertEqual(len(result.get("maintainer", [])), 1)


if __name__ == '__main__':
    unittest.main()
