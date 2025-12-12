#!/usr/bin/env python3
"""
CodeMeta property module for extracting version information from a GitHub repository.

This module extracts the current version of a software project using multiple strategies:
1. From GitHub releases (most reliable)
2. From git tags (semantic versioning)
3. From setup.py version field
4. From pyproject.toml version field
5. From package.json version field
6. From VERSION or version.txt files
7. From __init__.py __version__ attribute (Python)
8. From Cargo.toml version field (Rust)

The module attempts to extract semantic version information and validates version formats.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List
import re
import json
import requests

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content, get_github_token
from src.utils import normalize_url


# Semantic versioning regex pattern
SEMVER_PATTERN = r'^v?(\d+\.\d+\.\d+(?:[-+][\w.]+)?)$'
SIMPLE_VERSION_PATTERN = r'(\d+\.\d+(?:\.\d+)?(?:[-+][\w.]*)?)'


def is_valid_version(version_str: str) -> bool:
    """
    Check if a string is a valid version number.

    Args:
        version_str (str): The version string to validate.

    Returns:
        bool: True if the string appears to be a valid version number.
    """
    if not version_str:
        return False

    version_str = version_str.strip()

    # Check for semantic versioning pattern
    if re.match(SEMVER_PATTERN, version_str):
        return True

    # Check for simple version pattern
    if re.match(SIMPLE_VERSION_PATTERN, version_str):
        return True

    return False


def normalize_version(version_str: str) -> str:
    """
    Normalize a version string by removing common prefixes.

    Args:
        version_str (str): The version string to normalize.

    Returns:
        str: The normalized version string.
    """
    if not version_str:
        return ""

    # Remove leading/trailing whitespace and quotes
    version_str = version_str.strip().strip('"\'')

    # Remove common prefixes
    if version_str.startswith('v'):
        version_str = version_str[1:]

    return version_str.strip()


def extract_version_from_releases(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from GitHub releases.

    This is the most reliable source as releases are explicitly tagged
    and published by the project maintainers.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The latest release version or None if not found.
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
            tag_name = release_data.get("tag_name", "")

            if tag_name and is_valid_version(tag_name):
                return normalize_version(tag_name)

        return None

    except Exception:
        return None


def extract_version_from_tags(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from git tags.

    This function fetches git tags and looks for semantic version tags.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The latest semantic version tag or None if not found.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        # Fetch tags
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        response = requests.get(url, headers=headers, timeout=10, params={"per_page": 10})

        if response.status_code == 200:
            tags = response.json()

            for tag in tags:
                tag_name = tag.get("name", "")

                if tag_name and is_valid_version(tag_name):
                    return normalize_version(tag_name)

        return None

    except Exception:
        return None


def extract_version_from_setup_py(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from setup.py file (Python projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The version string or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "setup.py")
        if not content:
            return None

        # Look for version= parameter
        patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',
            r'version\s*=\s*version\s*=\s*["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                version = match.group(1).strip()
                if is_valid_version(version):
                    return normalize_version(version)

        return None

    except Exception:
        return None


def extract_version_from_pyproject_toml(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from pyproject.toml file (modern Python projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The version string or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "pyproject.toml")
        if not content:
            return None

        # Look for version field in [project] or [tool.poetry]
        patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                version = match.group(1).strip()
                if is_valid_version(version):
                    return normalize_version(version)

        return None

    except Exception:
        return None


def extract_version_from_package_json(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from package.json file (Node.js projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The version string or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "package.json")
        if not content:
            return None

        package_data = json.loads(content)
        version = package_data.get("version")

        if version and is_valid_version(version):
            return normalize_version(version)

        return None

    except Exception:
        return None


def extract_version_from_cargo_toml(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from Cargo.toml file (Rust projects).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The version string or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "Cargo.toml")
        if not content:
            return None

        # Look for version field
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1).strip()
            if is_valid_version(version):
                return normalize_version(version)

        return None

    except Exception:
        return None


def extract_version_from_version_file(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from VERSION or version.txt files.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The version string or None if not found.
    """
    version_files = ["VERSION", "version.txt", "VERSION.txt", "version", "VERSION.md"]

    for version_file in version_files:
        try:
            content = fetch_file_content(owner, repo, version_file)
            if content:
                # Extract the first line and clean it
                first_line = content.strip().split('\n')[0].strip()

                if is_valid_version(first_line):
                    return normalize_version(first_line)

        except Exception:
            continue

    return None


def extract_version_from_init_py(owner: str, repo: str) -> Optional[str]:
    """
    Extract version from __init__.py file (Python packages).

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The version string or None if not found.
    """
    try:
        content = fetch_file_content(owner, repo, "src/__init__.py")
        if not content:
            # Try alternative location
            content = fetch_file_content(owner, repo, "__init__.py")

        if not content:
            return None

        # Look for __version__ attribute
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1).strip()
            if is_valid_version(version):
                return normalize_version(version)

        return None

    except Exception:
        return None


def get(repository_url: str) -> Dict:
    """
    Extract version information from a GitHub repository.

    This function uses multiple strategies to extract the version:
    1. From GitHub releases (most reliable)
    2. From git tags (semantic versioning)
    3. From setup.py version field
    4. From pyproject.toml version field
    5. From package.json version field
    6. From VERSION or version.txt files
    7. From __init__.py __version__ attribute (Python)
    8. From Cargo.toml version field (Rust)

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'version' property and its value.
              Returns an empty dict if no version can be extracted.

    Example:
        >>> result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        >>> print(result)
        {'version': '1.0.0'}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    version = None

    # Strategy 1: Try GitHub releases (most reliable)
    version = extract_version_from_releases(owner, repo)
    if version:
        return {"version": version}

    # Strategy 2: Try git tags
    version = extract_version_from_tags(owner, repo)
    if version:
        return {"version": version}

    # Strategy 3: Try setup.py
    version = extract_version_from_setup_py(owner, repo)
    if version:
        return {"version": version}

    # Strategy 4: Try pyproject.toml
    version = extract_version_from_pyproject_toml(owner, repo)
    if version:
        return {"version": version}

    # Strategy 5: Try package.json
    version = extract_version_from_package_json(owner, repo)
    if version:
        return {"version": version}

    # Strategy 6: Try VERSION files
    version = extract_version_from_version_file(owner, repo)
    if version:
        return {"version": version}

    # Strategy 7: Try __init__.py
    version = extract_version_from_init_py(owner, repo)
    if version:
        return {"version": version}

    # Strategy 8: Try Cargo.toml
    version = extract_version_from_cargo_toml(owner, repo)
    if version:
        return {"version": version}

    return {}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/rsiebes/sshoc-nl-codemeta-generator",
        "https://github.com/openai/gpt-2",
        "https://github.com/tensorflow/tensorflow",
    ]

    for repo_url in test_repos:
        print(f"\nTesting: {repo_url}")
        result = get(repo_url)
        if result:
            print(f"Version: {result.get('version', 'N/A')}")
        else:
            print("No version found")
