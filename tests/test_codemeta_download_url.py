"""
Unit tests for the CodeMeta Download URL Module
"""

import unittest
from unittest.mock import patch, MagicMock
from src.modules import codemeta_download_url


class TestDownloadUrlExtraction(unittest.TestCase):
    """Test download URL extraction from releases."""

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_download_urls_from_releases(self, mock_fetch):
        """Test extraction of download URLs from releases."""
        mock_fetch.return_value = [
            {
                "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
                "tag_name": "v1.0.0",
                "assets": [
                    {
                        "browser_download_url": "https://github.com/owner/repo/releases/download/v1.0.0/app.tar.gz",
                        "name": "app.tar.gz"
                    },
                    {
                        "browser_download_url": "https://github.com/owner/repo/releases/download/v1.0.0/app.zip",
                        "name": "app.zip"
                    }
                ]
            }
        ]
        
        result = codemeta_download_url.extract_download_urls_from_releases("owner", "repo")
        
        self.assertEqual(len(result), 3)
        self.assertIn("https://github.com/owner/repo/releases/tag/v1.0.0", result)
        self.assertIn("https://github.com/owner/repo/releases/download/v1.0.0/app.tar.gz", result)
        self.assertIn("https://github.com/owner/repo/releases/download/v1.0.0/app.zip", result)

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_download_urls_no_releases(self, mock_fetch):
        """Test when no releases are found."""
        mock_fetch.return_value = None
        
        result = codemeta_download_url.extract_download_urls_from_releases("owner", "repo")
        
        self.assertEqual(result, [])

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_download_urls_no_assets(self, mock_fetch):
        """Test releases without assets."""
        mock_fetch.return_value = [
            {
                "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
                "tag_name": "v1.0.0",
                "assets": []
            }
        ]
        
        result = codemeta_download_url.extract_download_urls_from_releases("owner", "repo")
        
        self.assertEqual(len(result), 1)
        self.assertIn("https://github.com/owner/repo/releases/tag/v1.0.0", result)

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_download_urls_deduplication(self, mock_fetch):
        """Test that duplicate URLs are removed."""
        mock_fetch.return_value = [
            {
                "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
                "assets": []
            },
            {
                "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
                "assets": []
            }
        ]
        
        result = codemeta_download_url.extract_download_urls_from_releases("owner", "repo")
        
        self.assertEqual(len(result), 1)


class TestLatestReleaseUrl(unittest.TestCase):
    """Test latest release URL extraction."""

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_latest_release_url(self, mock_fetch):
        """Test extraction of latest release URL."""
        mock_fetch.return_value = [
            {
                "html_url": "https://github.com/owner/repo/releases/tag/v2.0.0",
                "tag_name": "v2.0.0"
            }
        ]
        
        result = codemeta_download_url.extract_latest_release_url("owner", "repo")
        
        self.assertEqual(result, "https://github.com/owner/repo/releases/tag/v2.0.0")

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_latest_release_url_no_releases(self, mock_fetch):
        """Test when no releases are found."""
        mock_fetch.return_value = None
        
        result = codemeta_download_url.extract_latest_release_url("owner", "repo")
        
        self.assertIsNone(result)

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_latest_release_url_empty_list(self, mock_fetch):
        """Test when releases list is empty."""
        mock_fetch.return_value = []
        
        result = codemeta_download_url.extract_latest_release_url("owner", "repo")
        
        self.assertIsNone(result)


class TestReleaseAssetUrls(unittest.TestCase):
    """Test release asset URL extraction."""

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_release_asset_urls(self, mock_fetch):
        """Test extraction of release asset URLs with metadata."""
        mock_fetch.return_value = [
            {
                "tag_name": "v1.0.0",
                "name": "Release 1.0.0",
                "assets": [
                    {
                        "browser_download_url": "https://github.com/owner/repo/releases/download/v1.0.0/app.tar.gz",
                        "name": "app.tar.gz",
                        "size": 1024000,
                        "download_count": 100,
                        "content_type": "application/gzip"
                    }
                ]
            }
        ]
        
        result = codemeta_download_url.extract_release_asset_urls("owner", "repo")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], "https://github.com/owner/repo/releases/download/v1.0.0/app.tar.gz")
        self.assertEqual(result[0]["name"], "app.tar.gz")
        self.assertEqual(result[0]["size"], 1024000)
        self.assertEqual(result[0]["release_tag"], "v1.0.0")

    @patch('src.modules.codemeta_download_url.fetch_repository_releases')
    def test_extract_release_asset_urls_no_releases(self, mock_fetch):
        """Test when no releases are found."""
        mock_fetch.return_value = None
        
        result = codemeta_download_url.extract_release_asset_urls("owner", "repo")
        
        self.assertEqual(result, [])


class TestDistributionUrls(unittest.TestCase):
    """Test distribution URL extraction."""

    @patch('src.modules.codemeta_download_url.extract_download_urls_from_releases')
    def test_get_distribution_urls(self, mock_extract):
        """Test extraction of distribution URLs."""
        mock_extract.return_value = [
            "https://github.com/owner/repo/releases/tag/v1.0.0"
        ]
        
        result = codemeta_download_url.get_distribution_urls("owner", "repo")
        
        self.assertGreater(len(result), 0)
        self.assertIn("https://github.com/owner/repo/releases/tag/v1.0.0", result)
        self.assertIn("https://pypi.org/project/repo/", result)
        self.assertIn("https://www.npmjs.com/package/repo", result)
        self.assertIn("https://github.com/owner/repo/releases", result)

    @patch('src.modules.codemeta_download_url.extract_download_urls_from_releases')
    def test_get_distribution_urls_deduplication(self, mock_extract):
        """Test that duplicate distribution URLs are removed."""
        mock_extract.return_value = []
        
        result = codemeta_download_url.get_distribution_urls("owner", "repo")
        
        # Check for duplicates
        self.assertEqual(len(result), len(set(result)))


class TestMainDownloadUrlFunction(unittest.TestCase):
    """Test the main get() function."""

    @patch('src.modules.codemeta_download_url.extract_download_urls_from_releases')
    @patch('src.modules.codemeta_download_url.parse_repository_url')
    def test_get_download_urls(self, mock_parse, mock_extract):
        """Test the main get() function."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = [
            "https://github.com/owner/repo/releases/tag/v1.0.0",
            "https://github.com/owner/repo/releases/download/v1.0.0/app.tar.gz"
        ]
        
        result = codemeta_download_url.get("https://github.com/owner/repo")
        
        self.assertIn("downloadUrl", result)
        self.assertEqual(len(result["downloadUrl"]), 2)

    @patch('src.modules.codemeta_download_url.extract_download_urls_from_releases')
    @patch('src.modules.codemeta_download_url.parse_repository_url')
    def test_get_no_download_urls(self, mock_parse, mock_extract):
        """Test when no download URLs are found."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = []
        
        result = codemeta_download_url.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_download_url.parse_repository_url')
    def test_get_invalid_url(self, mock_parse):
        """Test with invalid repository URL."""
        mock_parse.return_value = (None, None)
        
        result = codemeta_download_url.get("invalid-url")
        
        self.assertEqual(result, {})


class TestDownloadUrlDataValidation(unittest.TestCase):
    """Test download URL data validation."""

    @patch('src.modules.codemeta_download_url.extract_download_urls_from_releases')
    @patch('src.modules.codemeta_download_url.parse_repository_url')
    def test_download_urls_are_strings(self, mock_parse, mock_extract):
        """Test that all download URLs are strings."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = [
            "https://github.com/owner/repo/releases/tag/v1.0.0",
            "https://github.com/owner/repo/releases/download/v1.0.0/app.tar.gz"
        ]
        
        result = codemeta_download_url.get("https://github.com/owner/repo")
        
        for url in result.get("downloadUrl", []):
            self.assertIsInstance(url, str)
            self.assertTrue(url.startswith("https://"))

    @patch('src.modules.codemeta_download_url.extract_download_urls_from_releases')
    @patch('src.modules.codemeta_download_url.parse_repository_url')
    def test_download_urls_are_valid(self, mock_parse, mock_extract):
        """Test that download URLs are valid."""
        mock_parse.return_value = ("owner", "repo")
        mock_extract.return_value = [
            "https://github.com/owner/repo/releases/tag/v1.0.0"
        ]
        
        result = codemeta_download_url.get("https://github.com/owner/repo")
        
        for url in result.get("downloadUrl", []):
            self.assertIn("://", url)
            self.assertGreater(len(url), 10)


if __name__ == '__main__':
    unittest.main()
