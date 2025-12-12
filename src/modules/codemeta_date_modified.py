"""
CodeMeta Date Modified Module

This module extracts the last modification date of a GitHub repository.
It provides the date when the repository was last updated.
"""

from datetime import datetime
from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_info
)


def get_modification_date_from_api(owner: str, repo: str) -> Optional[str]:
    """
    Get repository last modification date from GitHub API.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: ISO 8601 formatted modification date or None.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        # Try updated_at first (most recent update)
        updated_at = repo_info.get("updated_at")
        if not updated_at:
            return None

        # Parse and validate the date
        try:
            # GitHub returns ISO 8601 format with Z suffix
            date_obj = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            # Return in ISO 8601 format (YYYY-MM-DD)
            return date_obj.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract last modification date from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'dateModified' key if date is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Get modification date from GitHub API
    modification_date = get_modification_date_from_api(owner, repo)

    if not modification_date:
        return {}

    return {
        "dateModified": modification_date
    }
