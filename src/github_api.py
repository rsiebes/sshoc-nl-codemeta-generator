#!/usr/bin/env python3
"""
GitHub API utilities for fetching repository information.
"""

import os
import re
from typing import Dict, Optional, Tuple
import requests

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

def parse_repository_url(repository_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a GitHub repository URL to extract owner and repo name.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple of (owner, repo) or (None, None) if invalid.
    """
    # Match both https://github.com/owner/repo and git@github.com:owner/repo formats
    patterns = [
        r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$"
    ]

    for pattern in patterns:
        match = re.match(pattern, repository_url)
        if match:
            return match.group(1), match.group(2)

    return None, None

def get_github_token() -> Optional[str]:
    """
    Get the GitHub API token from environment variables.

    Returns:
        Optional[str]: The GitHub API token or None if not set.
    """
    return os.environ.get("GITHUB_TOKEN")

def fetch_repository_info(owner: str, repo: str) -> Optional[Dict]:
    """
    Fetch repository information from the GitHub API.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: The repository information or None if the request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    headers = {}

    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching repository info: {e}")
        return None

def fetch_repository_languages(owner: str, repo: str) -> Optional[Dict]:
    """
    Fetch programming languages used in the repository.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[Dict]: A dictionary of languages and their byte counts or None if the request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    headers = {}

    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching repository languages: {e}")
        return None

def fetch_repository_contributors(owner: str, repo: str, per_page: int = 100) -> Optional[list]:
    """
    Fetch contributors of the repository.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        per_page (int): Number of results per page (max 100).

    Returns:
        Optional[list]: A list of contributors or None if the request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors"
    headers = {}

    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, params={"per_page": per_page}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching repository contributors: {e}")
        return None

def fetch_repository_releases(owner: str, repo: str, per_page: int = 100) -> Optional[list]:
    """
    Fetch releases of the repository.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        per_page (int): Number of results per page (max 100).

    Returns:
        Optional[list]: A list of releases or None if the request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases"
    headers = {}

    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, params={"per_page": per_page}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching repository releases: {e}")
        return None

def fetch_file_content(owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[str]:
    """
    Fetch the content of a file from the repository.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        file_path (str): The path to the file in the repository.
        branch (str): The branch to fetch from (default: main).

    Returns:
        Optional[str]: The file content or None if the request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{file_path}"
    headers = {}

    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, params={"ref": branch}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "content" in data:
            import base64
            return base64.b64decode(data["content"]).decode("utf-8")
        return None
    except requests.RequestException as e:
        print(f"Error fetching file content: {e}")
        return None
