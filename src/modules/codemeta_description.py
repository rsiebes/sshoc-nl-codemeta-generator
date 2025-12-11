#!/usr/bin/env python3
"""
CodeMeta property module for extracting software description.

This module extracts a detailed project description from a GitHub repository using
multiple strategies:
1. From the README.md file (comprehensive description from introduction section)
2. From the GitHub repository metadata (description field)
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


def extract_description_from_readme(owner: str, repo: str) -> Optional[str]:
    """
    Extract a comprehensive project description from README.md.

    This function extracts the introduction/description section of the README,
    which typically includes:
    1. The first paragraph after the main heading
    2. Additional paragraphs that describe the project's purpose and goals
    3. Stops at the first major section (Installation, Usage, etc.)

    The goal is to capture a rich, multi-sentence description that explains
    what the project does and why it exists.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[str]: The project description or None if not found.
    """
    content = fetch_file_content(owner, repo, "README.md")
    if not content:
        return None

    lines = content.split('\n')
    description_lines = []
    in_description = False
    blank_line_count = 0
    max_blank_lines = 2
    skip_badges = True
    found_real_content = False
    
    for i, line in enumerate(lines):
        # Skip until we find the main heading
        if not in_description:
            if line.startswith('# '):
                in_description = True
            continue
        
        # Stop at the next major heading
        if line.startswith('#'):
            break
        
        # Stop at code blocks
        if line.startswith('```'):
            break
        
        # Check if this is a badge/metadata line
        is_badge = line.strip().startswith('[![') or line.strip().startswith('[!') or line.strip().startswith('![') or line.strip().startswith('<')
        
        # Track blank lines
        if not line.strip():
            blank_line_count += 1
            if blank_line_count > max_blank_lines and found_real_content:
                break
            if found_real_content:
                description_lines.append(line)
            continue
        
        # Skip badge lines at the beginning
        if is_badge and not found_real_content:
            continue
        
        # Mark that we found real content
        if not is_badge:
            found_real_content = True
        
        # Reset blank line counter
        blank_line_count = 0
        
        # Add the line
        if found_real_content:
            description_lines.append(line)
    
    # Join lines and clean up
    description = '\n'.join(description_lines).strip()
    
    # Remove HTML tags and markdown formatting
    description = re.sub(r'<[^>]+>', '', description)
    description = re.sub(r'!\[([^\]]+)\]\([^\)]*\)', r'\1', description)  # Images
    description = re.sub(r'\[([^\]]+)\]\([^\)]*\)', r'\1', description)  # Links
    description = re.sub(r'\]\([^\)]*\)', '', description)  # Remaining incomplete links
    description = re.sub(r'\[', '', description)  # Remaining opening brackets
    description = re.sub(r'`([^`]+)`', r'\1', description)
    description = re.sub(r'\*\*([^\*]+)\*\*', r'\1', description)
    description = re.sub(r'\*([^\*]+)\*', r'\1', description)
    description = re.sub(r'__([^_]+)__', r'\1', description)
    description = re.sub(r'_([^_]+)_', r'\1', description)
    
    # Remove excessive whitespace
    description = re.sub(r'\n\s*\n+', ' ', description)
    description = re.sub(r'\s+', ' ', description)
    description = description.strip()
    
    # Remove empty brackets and badge remnants
    description = re.sub(r'\[\s*\]\(.*?\)', '', description)
    description = re.sub(r'\s+', ' ', description)
    description = description.strip()
    
    # Remove common badge text patterns
    description = re.sub(r'\btest\b\s+', '', description, flags=re.IGNORECASE)
    description = re.sub(r'\bDOI\b\s+', '', description)
    description = re.sub(r'\bProject Status:.*?developed\.\s*', '', description, flags=re.IGNORECASE)
    description = re.sub(r'\s+', ' ', description)
    description = description.strip()
    
    # Return only if we have a reasonable description
    if description and len(description) > 50:
        return description
    
    return None


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

    description = repo_info.get("description")
    if description and description.strip():
        return description.strip()

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

    match = re.search(r'long_description\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
    if match:
        description = match.group(1).strip()
        if description:
            return description

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

    match = re.search(r'\[metadata\].*?long_description\s*=\s*(.+?)(?=\n\[|\Z)', content, re.DOTALL)
    if match:
        description = match.group(1).strip()
        if description:
            return description

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

    This function uses multiple strategies to extract a rich description:
    1. From README.md (comprehensive introduction section) - PRIORITY
    2. From GitHub repository metadata (description field)
    3. From setup.py (long_description or description)
    4. From setup.cfg (long_description or description)
    5. From pyproject.toml (description)
    6. From package.json (description)

    The goal is to provide a rich, multi-sentence description that explains
    what the project does and its purpose. README extraction is prioritized
    because it typically contains the most comprehensive description.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'description' property and its value.
              Returns an empty dict if the description cannot be extracted.

    Example:
        >>> result = get("https://github.com/sodascience/osmenrich")
        >>> print(result)
        {'description': 'The goal of osmenrich is to easily enrich geocoded data...'}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    description = None

    # Strategy 1: Try README.md first
    description = extract_description_from_readme(owner, repo)
    if description:
        return {"description": description}

    # Strategy 2: Try GitHub repository metadata
    description = extract_description_from_repository_info(owner, repo)
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

    return {}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/sodascience/osmenrich",
        "https://github.com/python/cpython",
    ]

    for repo_url in test_repos:
        result = get(repo_url)
        if result:
            print(f"Repository: {repo_url}")
            print(f"Description: {result.get('description')}")
            print()
        else:
            print(f"Failed to extract description from {repo_url}")
