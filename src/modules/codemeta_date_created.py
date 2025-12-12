"""
CodeMeta Date Created Module

This module extracts the creation date of a GitHub repository.
It provides the date when the repository was first created.
"""

from datetime import datetime
from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_info
)


def get_creation_date_from_api(owner: str, repo: str) -> Optional[str]:
    """
    Get repository creation date from GitHub API.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: ISO 8601 formatted creation date or None.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        created_at = repo_info.get("created_at")
        if not created_at:
            return None

        # Parse and validate the date
        try:
            # GitHub returns ISO 8601 format with Z suffix
            date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            # Return in ISO 8601 format (YYYY-MM-DD)
            return date_obj.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract creation date from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'dateCreated' key if date is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Get creation date from GitHub API
    creation_date = get_creation_date_from_api(owner, repo)

    if not creation_date:
        return {}

    return {
        "dateCreated": creation_date
    }
