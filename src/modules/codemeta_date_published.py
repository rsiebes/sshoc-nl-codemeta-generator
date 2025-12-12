#!/usr/bin/env python3
"""
CodeMeta property module for extracting the publication date from a GitHub repository.

This module extracts the date when the software was published using multiple strategies:
1. From GitHub releases (most reliable)
2. From the latest commit to the default branch
3. From the repository creation date (fallback)

The module returns ISO 8601 formatted dates (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
"""

import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import requests

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, get_github_token
from src.utils import normalize_url


def is_valid_iso_date(date_str: str) -> bool:
    """
    Check if a string is a valid ISO 8601 date.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if the string is a valid ISO 8601 date.
    """
    if not date_str:
        return False

    try:
        # Try to parse ISO 8601 format
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize a date string to ISO 8601 format (YYYY-MM-DD).

    Args:
        date_str (str): The date string to normalize.

    Returns:
        Optional[str]: The normalized date string or None if invalid.
    """
    if not date_str:
        return None

    try:
        # Parse the date string
        if 'T' in date_str:
            # ISO 8601 format with time
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Date only format
            dt = datetime.fromisoformat(date_str)

        # Return in ISO 8601 date format (YYYY-MM-DD)
        return dt.strftime('%Y-%m-%d')

    except (ValueError, AttributeError):
        return None


def extract_date_from_latest_release(owner: str, repo: str) -> Optional[str]:
    """
    Extract the publication date from the latest GitHub release.

    This is the most reliable source as releases are explicitly published
    with a specific date.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The publication date in ISO 8601 format or None if not found.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        # Fetch the latest release
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            release_data = response.json()
            # Try published_at first, then created_at
            published_at = release_data.get("published_at") or release_data.get("created_at")

            if published_at:
                return normalize_date(published_at)

        return None

    except Exception:
        return None


def extract_date_from_latest_commit(owner: str, repo: str) -> Optional[str]:
    """
    Extract the date of the latest commit to the default branch.

    This provides a fallback when releases are not available.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The commit date in ISO 8601 format or None if not found.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        # Fetch the latest commit
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        response = requests.get(url, headers=headers, timeout=10, params={"per_page": 1})

        if response.status_code == 200:
            commits = response.json()

            if commits and isinstance(commits, list) and len(commits) > 0:
                commit = commits[0]
                commit_date = commit.get("commit", {}).get("committer", {}).get("date")

                if commit_date:
                    return normalize_date(commit_date)

        return None

    except Exception:
        return None


def extract_date_from_repository_creation(owner: str, repo: str) -> Optional[str]:
    """
    Extract the repository creation date.

    This is a fallback when other methods don't return a date.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The creation date in ISO 8601 format or None if not found.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        created_at = repo_info.get("created_at")

        if created_at:
            return normalize_date(created_at)

        return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract the publication date from a GitHub repository.

    This function uses multiple strategies to extract the publication date:
    1. From GitHub releases (most reliable)
    2. From the latest commit to the default branch
    3. From the repository creation date (fallback)

    The returned date is in ISO 8601 format (YYYY-MM-DD).

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'datePublished' property and its value.
              Returns an empty dict if no date can be extracted.

    Example:
        >>> result = get("https://github.com/tensorflow/tensorflow")
        >>> print(result)
        {'datePublished': '2024-01-15'}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    date = None

    # Strategy 1: Try latest release (most reliable)
    date = extract_date_from_latest_release(owner, repo)
    if date:
        return {"datePublished": date}

    # Strategy 2: Try latest commit
    date = extract_date_from_latest_commit(owner, repo)
    if date:
        return {"datePublished": date}

    # Strategy 3: Try repository creation date (fallback)
    date = extract_date_from_repository_creation(owner, repo)
    if date:
        return {"datePublished": date}

    return {}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/tensorflow/tensorflow",
        "https://github.com/openai/gpt-2",
        "https://github.com/rust-lang/rust",
    ]

    for repo_url in test_repos:
        print(f"\nTesting: {repo_url}")
        result = get(repo_url)
        if result:
            print(f"Date Published: {result.get('datePublished', 'N/A')}")
        else:
            print("No date found")
