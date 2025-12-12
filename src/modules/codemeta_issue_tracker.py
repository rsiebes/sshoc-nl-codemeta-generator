"""
CodeMeta Issue Tracker Module

This module extracts the issue tracker information from a GitHub repository.
It provides the URL to the repository's issue tracker.
"""

from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_info
)


def get_issue_tracker_url(owner: str, repo: str) -> Optional[str]:
    """
    Get issue tracker URL from GitHub repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Issue tracker URL or None.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        # Check if issues are enabled
        has_issues = repo_info.get("has_issues", False)
        if not has_issues:
            return None

        # Construct the GitHub issues URL
        # Format: https://github.com/owner/repo/issues
        issues_url = f"https://github.com/{owner}/{repo}/issues"
        return issues_url

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract issue tracker information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'issueTracker' key if issue tracker is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Get issue tracker URL
    issue_tracker_url = get_issue_tracker_url(owner, repo)

    if not issue_tracker_url:
        return {}

    return {
        "issueTracker": issue_tracker_url
    }
