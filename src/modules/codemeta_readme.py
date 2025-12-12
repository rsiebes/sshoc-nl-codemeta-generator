"""
CodeMeta README Module

This module extracts the README content from a GitHub repository.
It provides the raw README file content or a URL to the README.
"""

from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_file_content
)


def get_readme_content(owner: str, repo: str) -> Optional[str]:
    """
    Get README content from GitHub repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: README content or None.
    """
    try:
        # Try to fetch README.md first
        readme_content = fetch_file_content(owner, repo, "README.md")
        if readme_content:
            return readme_content

        # Try README.rst as fallback
        readme_content = fetch_file_content(owner, repo, "README.rst")
        if readme_content:
            return readme_content

        # Try README.txt as fallback
        readme_content = fetch_file_content(owner, repo, "README.txt")
        if readme_content:
            return readme_content

        # Try README (no extension) as fallback
        readme_content = fetch_file_content(owner, repo, "README")
        if readme_content:
            return readme_content

        return None

    except Exception:
        return None


def get_readme_url(owner: str, repo: str) -> Optional[str]:
    """
    Get README URL from GitHub repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: README URL or None.
    """
    try:
        # Construct the GitHub raw content URL for README.md
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
        return readme_url

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract README information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'readme' key if README is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Get README content
    readme_content = get_readme_content(owner, repo)

    if not readme_content:
        return {}

    return {
        "readme": readme_content
    }
