"""
Unit tests for codemeta_issue_tracker module.
"""

import unittest
from unittest.mock import patch
from src.modules import codemeta_issue_tracker


class TestIssueTrackerExtraction(unittest.TestCase):
    """Test issue tracker extraction."""

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_basic_issue_tracker_extraction(self, mock_fetch):
        """Test extraction of basic issue tracker URL."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/owner/repo/issues")

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_disabled(self, mock_fetch):
        """Test handling of disabled issue tracker."""
        mock_fetch.return_value = {
            "has_issues": False
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_not_specified(self, mock_fetch):
        """Test handling of unspecified issue tracker status."""
        mock_fetch.return_value = {}
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_none_repository_info(self, mock_fetch):
        """Test handling of None repository info."""
        mock_fetch.return_value = None
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_api_error_handling(self, mock_fetch):
        """Test handling of API errors."""
        mock_fetch.side_effect = Exception("API Error")
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_invalid_url_handling(self, mock_fetch):
        """Test handling of invalid repository URL."""
        result = codemeta_issue_tracker.get("invalid-url")
        
        self.assertEqual(result, {})


class TestIssueTrackerContent(unittest.TestCase):
    """Test issue tracker content validation."""

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_is_string(self, mock_fetch):
        """Test that issue tracker URL is a string."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertIn("issueTracker", result)
        self.assertIsInstance(result["issueTracker"], str)

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_not_empty(self, mock_fetch):
        """Test that issue tracker URL is not empty."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertIn("issueTracker", result)
        self.assertTrue(result["issueTracker"])

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_url_format(self, mock_fetch):
        """Test that issue tracker URL has correct format."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertIn("issueTracker", result)
        url = result["issueTracker"]
        self.assertTrue(url.startswith("https://github.com/"))
        self.assertTrue(url.endswith("/issues"))

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_contains_owner_and_repo(self, mock_fetch):
        """Test that issue tracker URL contains owner and repo."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("issueTracker", result)
        url = result["issueTracker"]
        self.assertIn("tensorflow", url)


class TestRealRepositories(unittest.TestCase):
    """Test issue tracker extraction from real repositories."""

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_tensorflow_issue_tracker(self, mock_fetch):
        """Test issue tracker extraction from TensorFlow."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/tensorflow/tensorflow")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/tensorflow/tensorflow/issues")

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_flask_issue_tracker(self, mock_fetch):
        """Test issue tracker extraction from Flask."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/pallets/flask")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/pallets/flask/issues")

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_rust_issue_tracker(self, mock_fetch):
        """Test issue tracker extraction from Rust."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/rust-lang/rust")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/rust-lang/rust/issues")

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_dryad_issue_tracker(self, mock_fetch):
        """Test issue tracker extraction from Dryad."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/Dryad-lang/Dryad")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/Dryad-lang/Dryad/issues")


class TestIssueTrackerStatus(unittest.TestCase):
    """Test issue tracker status handling."""

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_enabled_true(self, mock_fetch):
        """Test handling of explicitly enabled issue tracker."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertIn("issueTracker", result)

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_issue_tracker_enabled_false(self, mock_fetch):
        """Test handling of explicitly disabled issue tracker."""
        mock_fetch.return_value = {
            "has_issues": False
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertEqual(result, {})

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_multiple_repositories_with_issues(self, mock_fetch):
        """Test extraction from multiple repositories with issues enabled."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        
        repos = [
            "https://github.com/owner1/repo1",
            "https://github.com/owner2/repo2",
            "https://github.com/owner3/repo3"
        ]
        
        for repo_url in repos:
            result = codemeta_issue_tracker.get(repo_url)
            self.assertIn("issueTracker", result)
            self.assertTrue(result["issueTracker"].endswith("/issues"))


class TestIssueTrackerURL(unittest.TestCase):
    """Test issue tracker URL construction."""

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_url_construction_format(self, mock_fetch):
        """Test that URL is constructed correctly."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo")
        
        self.assertIn("issueTracker", result)
        url = result["issueTracker"]
        # Should be: https://github.com/owner/repo/issues
        self.assertEqual(url, "https://github.com/owner/repo/issues")

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_url_with_special_characters_in_repo_name(self, mock_fetch):
        """Test URL construction with special characters in repo name."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner/repo-with-dashes")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/owner/repo-with-dashes/issues")

    @patch('src.modules.codemeta_issue_tracker.fetch_repository_info')
    def test_url_with_numbers_in_names(self, mock_fetch):
        """Test URL construction with numbers in owner/repo names."""
        mock_fetch.return_value = {
            "has_issues": True
        }
        result = codemeta_issue_tracker.get("https://github.com/owner123/repo456")
        
        self.assertIn("issueTracker", result)
        self.assertEqual(result["issueTracker"], "https://github.com/owner123/repo456/issues")


if __name__ == '__main__':
    unittest.main()
