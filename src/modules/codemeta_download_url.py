"""
CodeMeta Download URL Module

This module extracts download URLs and release information from a GitHub repository.
It identifies the latest release, release assets, and download locations.
"""

from typing import Dict, List, Optional
from src.github_api import (
    parse_repository_url,
    fetch_repository_releases,
)
import re


def extract_download_urls_from_releases(owner: str, repo: str) -> List[str]:
    """
    Extract download URLs from GitHub releases.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of download URLs from releases.
    """
    try:
        download_urls = []
        
        # Fetch releases from GitHub API
        releases = fetch_repository_releases(owner, repo, per_page=10)
        
        if not releases:
            return download_urls

        # Extract URLs from releases
        for release in releases:
            # Get the latest release URL
            if release.get("html_url"):
                download_urls.append(release.get("html_url"))
            
            # Get release asset URLs
            assets = release.get("assets", [])
            for asset in assets:
                if asset.get("browser_download_url"):
                    download_urls.append(asset.get("browser_download_url"))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in download_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        return unique_urls

    except Exception:
        return []


def extract_latest_release_url(owner: str, repo: str) -> Optional[str]:
    """
    Extract the latest release URL from GitHub.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        Optional[str]: URL of the latest release if found.
    """
    try:
        releases = fetch_repository_releases(owner, repo, per_page=1)
        
        if releases and len(releases) > 0:
            latest_release = releases[0]
            if latest_release.get("html_url"):
                return latest_release.get("html_url")
        
        return None

    except Exception:
        return None


def extract_release_asset_urls(owner: str, repo: str) -> List[Dict]:
    """
    Extract release asset URLs with metadata.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of release asset objects with URL and metadata.
    """
    try:
        asset_urls = []
        
        releases = fetch_repository_releases(owner, repo, per_page=5)
        
        if not releases:
            return asset_urls

        for release in releases:
            assets = release.get("assets", [])
            for asset in assets:
                asset_obj = {
                    "url": asset.get("browser_download_url"),
                    "name": asset.get("name"),
                    "size": asset.get("size"),
                    "download_count": asset.get("download_count"),
                    "content_type": asset.get("content_type"),
                    "release_tag": release.get("tag_name"),
                    "release_name": release.get("name")
                }
                asset_urls.append(asset_obj)
        
        return asset_urls

    except Exception:
        return []


def get_distribution_urls(owner: str, repo: str) -> List[str]:
    """
    Get distribution/package URLs from various sources.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[str]: List of distribution URLs.
    """
    try:
        distribution_urls = []
        
        # Get release URLs
        release_urls = extract_download_urls_from_releases(owner, repo)
        distribution_urls.extend(release_urls)
        
        # Add common package repository URLs
        # PyPI
        distribution_urls.append(f"https://pypi.org/project/{repo}/")
        
        # NPM
        distribution_urls.append(f"https://www.npmjs.com/package/{repo}")
        
        # GitHub releases page
        distribution_urls.append(f"https://github.com/{owner}/{repo}/releases")
        
        # GitHub archive URLs
        distribution_urls.append(f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip")
        distribution_urls.append(f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in distribution_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        return unique_urls

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract download URL information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'downloadUrl' key containing download URLs if found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Extract download URLs from releases
    download_urls = extract_download_urls_from_releases(owner, repo)
    
    if not download_urls:
        return {}

    # Return as array (CodeMeta allows array of download URLs)
    return {
        "downloadUrl": download_urls
    }
