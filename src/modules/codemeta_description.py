#!/usr/bin/env python3
"""
CodeMeta property module for extracting software description.

This module extracts a detailed project description from a GitHub repository using
multiple strategies:
1. From the GitHub repository metadata (description field)
2. From the README.md file (first paragraph after the title)
3. From setup.py or setup.cfg (long_description field)
4. From pyproject.toml (description field)
5. From package.json (description field)
"""

import sys
from pathlib import Path
from typing import Optional, Dict
import re
import json

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content
from src.utils import normalize_url


def extract_description_from_repository_info(owner: str, repo: str) -> Optional[str]:
    """
    Extract the project description from GitHub repository metadata.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The project description or None if not found.
    """
    repo_info = fetch_repository_info(owner, repo)
    if not repo_info:
        return None

    # Try to get the description from the repository metadata
    description = repo_info.get("description")
    if description and description.strip():
        return description.strip()

    return None


def extract_description_from_readme(owner: str, repo: str) -> Optional[str]:
    """
    Extract the project description from README.md.

    This function looks for the first paragraph after the main heading,
    which typically contains the project description.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The project description or None if not found.
    """
    content = fetch_file_content(owner, repo, "README.md")
    if not content:
        return None

    # Remove the first heading
    lines = content.split('\n')
    description_lines = []
    in_description = False
    skip_blank_lines = True

    for line in lines:
        # Skip the first heading
        if line.startswith('#') and not in_description:
            in_description = True
            continue

        if in_description:
            # Skip blank lines at the beginning
            if skip_blank_lines and not line.strip():
                continue

            # Stop at the next heading
            if line.startswith('#'):
                break

            # Stop at code blocks
            if line.startswith('```'):
                break

            # Stop at lists (unless we have content already)
            if description_lines and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                break

            skip_blank_lines = False
            description_lines.append(line)

    # Join lines and clean up
    description = '\n'.join(description_lines).strip()

    # Remove excessive whitespace
    description = re.sub(r'\n\s*\n', '\n', description)
    description = ' '.join(description.split())

    # Return only if we have a reasonable description (at least 10 characters)
    if description and len(description) > 10:
        return description

    return None


def extract_description_from_setup_py(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package description from setup.py.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package description or None if not found.
    """
    content = fetch_file_content(owner, repo, "setup.py")
    if not content:
        return None

    # Try to extract long_description from setup() call
    # Pattern: long_description="..." or long_description='...'
    match = re.search(r'long_description\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
    if match:
        description = match.group(1).strip()
        if description:
            return description

    # Try to extract description field
    match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        description = match.group(1).strip()
        if description:
            return description

    return None


def extract_description_from_setup_cfg(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package description from setup.cfg.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package description or None if not found.
    """
    content = fetch_file_content(owner, repo, "setup.cfg")
    if not content:
        return None

    # Try to extract long_description from [metadata] section
    match = re.search(r'\[metadata\].*?long_description\s*=\s*(.+?)(?=\n\[|\Z)', content, re.DOTALL)
    if match:
        description = match.group(1).strip()
        if description:
            return description

    # Try to extract description field
    match = re.search(r'\[metadata\].*?description\s*=\s*(.+?)(?=\n[a-z]|\Z)', content, re.DOTALL)
    if match:
        description = match.group(1).strip()
        if description:
            return description

    return None


def extract_description_from_pyproject_toml(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package description from pyproject.toml.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package description or None if not found.
    """
    content = fetch_file_content(owner, repo, "pyproject.toml")
    if not content:
        return None

    # Try to extract description from [project] section
    # Pattern: description = "..."
    match = re.search(r'\[project\].*?description\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
    if match:
        description = match.group(1).strip()
        if description:
            return description

    return None


def extract_description_from_package_json(owner: str, repo: str) -> Optional[str]:
    """
    Extract the package description from package.json.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The package description or None if not found.
    """
    content = fetch_file_content(owner, repo, "package.json")
    if not content:
        return None

    try:
        package_data = json.loads(content)
        description = package_data.get("description")
        if description and isinstance(description, str):
            return description.strip()
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def get(repository_url: str) -> Dict:
    """
    Extract the software description from a GitHub repository.

    This function uses multiple strategies to extract the description:
    1. From GitHub repository metadata (description field)
    2. From README.md (first paragraph after the title)
    3. From setup.py (long_description or description)
    4. From setup.cfg (long_description or description)
    5. From pyproject.toml (description)
    6. From package.json (description)

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'description' property and its value.
              Returns an empty dict if the description cannot be extracted.

    Example:
        >>> result = get("https://github.com/sodascience/osmenrich")
        >>> print(result)
        {'description': 'A tool to enrich geocoded data using OpenStreetMap...'}
    """
    # Normalize the URL
    repository_url = normalize_url(repository_url)

    # Parse the repository URL
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Try different strategies to extract the description
    description = None

    # Strategy 1: Try GitHub repository metadata
    description = extract_description_from_repository_info(owner, repo)
    if description:
        return {"description": description}

    # Strategy 2: Try README.md
    description = extract_description_from_readme(owner, repo)
    if description:
        return {"description": description}

    # Strategy 3: Try setup.py
    description = extract_description_from_setup_py(owner, repo)
    if description:
        return {"description": description}

    # Strategy 4: Try setup.cfg
    description = extract_description_from_setup_cfg(owner, repo)
    if description:
        return {"description": description}

    # Strategy 5: Try pyproject.toml
    description = extract_description_from_pyproject_toml(owner, repo)
    if description:
        return {"description": description}

    # Strategy 6: Try package.json
    description = extract_description_from_package_json(owner, repo)
    if description:
        return {"description": description}

    # If all strategies fail, return empty dict
    return {}


if __name__ == "__main__":
    # Example usage
    test_repos = [
        "https://github.com/sodascience/osmenrich",
        "https://github.com/python/cpython",
    ]

    for repo_url in test_repos:
        result = get(repo_url)
        if result:
            print(f"Repository: {repo_url}")
            print(f"Description: {result.get('description')[:100]}...")
            print()
        else:
            print(f"Failed to extract description from {repo_url}")
