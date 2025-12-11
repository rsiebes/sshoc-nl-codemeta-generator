#!/usr/bin/env python3
"""
CodeMeta property module for extracting software name.

This module extracts the software name from a GitHub repository using multiple strategies:
1. From the GitHub repository metadata (repository name)
2. From the setup.py or pyproject.toml file (package name)
3. From the README.md file (project title)
4. From the GitHub API repository name as fallback
"""

import sys
from pathlib import Path
from typing import Optional, Dict

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content
from src.utils import normalize_url
import re
import json


def extract_name_from_url(repository_url: str) -> Optional[str]:
    """
    Extract the repository name from the GitHub URL.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Optional[str]: The repository name or None if invalid.
    """
    owner, repo = parse_repository_url(repository_url)
    if repo:
        return repo
    return None


def extract_name_from_setup_py(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package name from setup.py.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package name or None if not found.
    """
    content = fetch_file_content(owner, repo, "setup.py")
    if not content:
        return None

    # Try to extract name from setup() call
    # Pattern: name="package-name" or name='package-name'
    match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    return None


def extract_name_from_pyproject_toml(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package name from pyproject.toml.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package name or None if not found.
    """
    content = fetch_file_content(owner, repo, "pyproject.toml")
    if not content:
        return None

    # Try to extract name from [project] section
    # Pattern: name = "package-name"
    match = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)

    return None


def extract_name_from_package_json(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package name from package.json.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package name or None if not found.
    """
    content = fetch_file_content(owner, repo, "package.json")
    if not content:
        return None

    try:
        package_data = json.loads(content)
        name = package_data.get("name")
        if name:
            return name
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def extract_name_from_readme(owner: str, repo: str) -> Optional[str]:
    """
    Extract the project name from README.md.

    This function looks for the first heading in the README file,
    which typically contains the project name.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The project name or None if not found.
    """
    content = fetch_file_content(owner, repo, "README.md")
    if not content:
        return None

    # Try to extract the first heading (# Project Name)
    match = re.search(r'^#\s+(.+?)(?:\s*\n|$)', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Remove markdown formatting
        title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title)  # Remove links
        title = re.sub(r'[*_`]', '', title)  # Remove bold/italic/code formatting
        return title

    return None


def extract_name_from_repository_info(owner: str, repo: str) -> Optional[str]:
    """
    Extract the project name from GitHub repository metadata.

    This function fetches the repository information from the GitHub API
    and extracts the name from various fields.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The project name or None if not found.
    """
    repo_info = fetch_repository_info(owner, repo)
    if not repo_info:
        return None

    # Try to get the name from the repository metadata
    # Priority: full_name > name > repo name
    name = repo_info.get("full_name") or repo_info.get("name")
    if name:
        return name

    return None


def get(repository_url: str) -> Dict:
    """
    Extract the software name from a GitHub repository.

    This function uses multiple strategies to extract the software name:
    1. From setup.py (Python projects)
    2. From pyproject.toml (Modern Python projects)
    3. From package.json (Node.js projects)
    4. From README.md (First heading)
    5. From GitHub repository metadata
    6. From the repository URL as fallback

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'name' property and its value.
              Returns an empty dict if the name cannot be extracted.

    Example:
        >>> result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        >>> print(result)
        {'name': 'sshoc-nl-codemeta-generator'}
    """
    # Normalize the URL
    repository_url = normalize_url(repository_url)

    # Parse the repository URL
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Try different strategies to extract the name
    name = None

    # Strategy 1: Try setup.py (Python projects)
    name = extract_name_from_setup_py(owner, repo)
    if name:
        return {"name": name}

    # Strategy 2: Try pyproject.toml (Modern Python projects)
    name = extract_name_from_pyproject_toml(owner, repo)
    if name:
        return {"name": name}

    # Strategy 3: Try package.json (Node.js projects)
    name = extract_name_from_package_json(owner, repo)
    if name:
        return {"name": name}

    # Strategy 4: Try README.md (First heading)
    name = extract_name_from_readme(owner, repo)
    if name:
        return {"name": name}

    # Strategy 5: Try GitHub repository metadata
    name = extract_name_from_repository_info(owner, repo)
    if name:
        return {"name": name}

    # Strategy 6: Fallback to repository name from URL
    name = extract_name_from_url(repository_url)
    if name:
        return {"name": name}

    # If all strategies fail, return empty dict
    return {}


if __name__ == "__main__":
    # Example usage
    test_repos = [
        "https://github.com/rsiebes/sshoc-nl-codemeta-generator",
        "https://github.com/python/cpython",
        "https://github.com/torvalds/linux",
    ]

    for repo_url in test_repos:
        result = get(repo_url)
        if result:
            print(f"Repository: {repo_url}")
            print(f"Name: {result.get('name')}")
            print()
        else:
            print(f"Failed to extract name from {repo_url}")
