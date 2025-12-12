"""
CodeMeta URL Module

This module extracts the project homepage URL from a GitHub repository.
It provides the official project website or homepage URL.
"""

from typing import Dict, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_info,
    fetch_file_content
)
import re


def validate_url(url: str) -> bool:
    """
    Validate if a URL is a valid HTTP/HTTPS URL.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True if URL is valid, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    
    # Check if it starts with http:// or https://
    if not (url.startswith("http://") or url.startswith("https://")):
        return False
    
    # Basic URL validation
    if len(url) < 10:  # Minimum length for a valid URL
        return False
    
    return True


def get_url_from_repository_info(owner: str, repo: str) -> Optional[str]:
    """
    Get homepage URL from GitHub repository info.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Homepage URL or None.
    """
    try:
        repo_info = fetch_repository_info(owner, repo)
        if not repo_info:
            return None

        # Check for homepage URL in repository info
        homepage = repo_info.get("homepage")
        if homepage and validate_url(homepage):
            return homepage

        return None

    except Exception:
        return None


def get_url_from_readme(owner: str, repo: str) -> Optional[str]:
    """
    Extract homepage URL from README file.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: Homepage URL or None.
    """
    try:
        readme_content = fetch_file_content(owner, repo, "README.md")
        if not readme_content:
            return None

        # Look for common URL patterns in README
        # Pattern 1: [text](url) - Markdown links
        markdown_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', readme_content)
        for text, url in markdown_links:
            # Look for homepage, website, or official links
            if any(keyword in text.lower() for keyword in ['homepage', 'website', 'official', 'demo', 'live']):
                if validate_url(url):
                    return url

        # Pattern 2: Direct URLs in text
        urls = re.findall(r'https?://[^\s\)\]]+', readme_content)
        for url in urls:
            # Clean up trailing punctuation
            url = url.rstrip('.,;:')
            if validate_url(url):
                # Prefer non-GitHub URLs
                if 'github.com' not in url:
                    return url

        return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract homepage URL from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'url' key if URL is found, empty dict otherwise.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Try multiple strategies in priority order
    strategies = [
        lambda: get_url_from_repository_info(owner, repo),
        lambda: get_url_from_readme(owner, repo),
    ]

    url = None
    for strategy in strategies:
        try:
            url = strategy()
            if url:
                break
        except Exception:
            continue

    if not url:
        return {}

    return {
        "url": url
    }
