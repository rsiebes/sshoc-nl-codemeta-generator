#!/usr/bin/env python3
"""
CodeMeta property module for extracting author information.

This module extracts author and contributor information from a GitHub repository using
multiple strategies:
1. From GitHub API contributors endpoint
2. From git commit history (first committer)
3. From setup.py author field
4. From pyproject.toml author field
5. From package.json author field
6. From ORCID registry (when available)

The module attempts to enrich author information with ORCID identifiers when possible.
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


def extract_authors_from_github_api(owner: str, repo: str, max_authors: int = 5) -> Optional[List[Dict]]:
    """
    Extract authors from GitHub API contributors endpoint.

    This function fetches the contributors list from GitHub and returns the top contributors.
    Each author includes: name, email (if available), GitHub URL, and attempts to find ORCID.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        max_authors (int): Maximum number of authors to extract (default: 5).

    Returns:
        Optional[List[Dict]]: A list of author dictionaries or None if not found.
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        headers = {}
        
        # Use GitHub token if available
        token = get_github_token()
        if token:
            headers["Authorization"] = f"token {token}"
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        contributors = response.json()

        if not contributors:
            return None

        authors = []
        for contributor in contributors[:max_authors]:
            author = {
                "name": contributor.get("login", ""),
                "@type": "Person",
                "url": contributor.get("html_url", ""),
            }

            # Try to get additional info from the user's GitHub profile
            user_url = contributor.get("url")
            if user_url:
                try:
                    user_headers = {}
                    if token:
                        user_headers["Authorization"] = f"token {token}"
                    
                    user_response = requests.get(user_url, headers=user_headers, timeout=10)
                    user_response.raise_for_status()
                    user_data = user_response.json()

                    # Add real name if available
                    if user_data.get("name"):
                        author["name"] = user_data.get("name")

                    # Add email if available
                    if user_data.get("email"):
                        author["email"] = user_data.get("email")

                    # Add affiliation if available
                    if user_data.get("company"):
                        author["affiliation"] = user_data.get("company")

                except Exception:
                    pass

            # Try to find ORCID identifier
            orcid = find_orcid_for_author(author.get("name", ""), author.get("email", ""))
            if orcid:
                author["@id"] = f"https://orcid.org/{orcid}"

            authors.append(author)

        return authors if authors else None

    except Exception as e:
        return None


def extract_authors_from_setup_py(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract author information from setup.py.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[List[Dict]]: A list of author dictionaries or None if not found.
    """
    content = fetch_file_content(owner, repo, "setup.py")
    if not content:
        return None

    authors = []

    # Try to extract author field
    match = re.search(r'author\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        author_name = match.group(1).strip()
        if author_name:
            author = {
                "name": author_name,
                "@type": "Person",
            }

            # Try to find ORCID
            orcid = find_orcid_for_author(author_name)
            if orcid:
                author["@id"] = f"https://orcid.org/{orcid}"

            authors.append(author)

    # Try to extract author_email field
    match = re.search(r'author_email\s*=\s*["\']([^"\']+)["\']', content)
    if match and authors:
        authors[0]["email"] = match.group(1).strip()

    # Try to extract maintainer field
    match = re.search(r'maintainer\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        maintainer_name = match.group(1).strip()
        if maintainer_name and maintainer_name != authors[0].get("name") if authors else True:
            author = {
                "name": maintainer_name,
                "@type": "Person",
            }

            # Try to find ORCID
            orcid = find_orcid_for_author(maintainer_name)
            if orcid:
                author["@id"] = f"https://orcid.org/{orcid}"

            authors.append(author)

    return authors if authors else None


def extract_authors_from_pyproject_toml(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract author information from pyproject.toml.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[List[Dict]]: A list of author dictionaries or None if not found.
    """
    content = fetch_file_content(owner, repo, "pyproject.toml")
    if not content:
        return None

    authors = []

    # Try to extract authors from [project] section
    # Pattern: authors = [{name = "...", email = "..."}]
    match = re.search(r'\[project\].*?authors\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if match:
        authors_section = match.group(1)
        # Extract individual author entries
        author_matches = re.findall(r'\{([^}]+)\}', authors_section)
        for author_match in author_matches:
            author = {"@type": "Person"}

            # Extract name
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', author_match)
            if name_match:
                author["name"] = name_match.group(1).strip()

            # Extract email
            email_match = re.search(r'email\s*=\s*["\']([^"\']+)["\']', author_match)
            if email_match:
                author["email"] = email_match.group(1).strip()

            if "name" in author:
                # Try to find ORCID
                orcid = find_orcid_for_author(author.get("name", ""), author.get("email", ""))
                if orcid:
                    author["@id"] = f"https://orcid.org/{orcid}"

                authors.append(author)

    return authors if authors else None


def extract_authors_from_package_json(owner: str, repo: str) -> Optional[List[Dict]]:
    """
    Extract author information from package.json.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        Optional[List[Dict]]: A list of author dictionaries or None if not found.
    """
    content = fetch_file_content(owner, repo, "package.json")
    if not content:
        return None

    try:
        package_data = json.loads(content)
        authors = []

        # Try to get author field
        if package_data.get("author"):
            author_data = package_data.get("author")
            author = {"@type": "Person"}

            if isinstance(author_data, str):
                # Parse "Name <email>" format
                match = re.match(r'([^<]+)\s*<([^>]+)>', author_data)
                if match:
                    author["name"] = match.group(1).strip()
                    author["email"] = match.group(2).strip()
                else:
                    author["name"] = author_data.strip()
            elif isinstance(author_data, dict):
                if author_data.get("name"):
                    author["name"] = author_data.get("name")
                if author_data.get("email"):
                    author["email"] = author_data.get("email")
                if author_data.get("url"):
                    author["url"] = author_data.get("url")

            if "name" in author:
                # Try to find ORCID
                orcid = find_orcid_for_author(author.get("name", ""), author.get("email", ""))
                if orcid:
                    author["@id"] = f"https://orcid.org/{orcid}"

                authors.append(author)

        # Try to get contributors field
        if package_data.get("contributors"):
            contributors = package_data.get("contributors", [])
            if isinstance(contributors, list):
                for contributor in contributors[:4]:  # Limit to 4 additional contributors
                    author = {"@type": "Person"}

                    if isinstance(contributor, str):
                        match = re.match(r'([^<]+)\s*<([^>]+)>', contributor)
                        if match:
                            author["name"] = match.group(1).strip()
                            author["email"] = match.group(2).strip()
                        else:
                            author["name"] = contributor.strip()
                    elif isinstance(contributor, dict):
                        if contributor.get("name"):
                            author["name"] = contributor.get("name")
                        if contributor.get("email"):
                            author["email"] = contributor.get("email")

                    if "name" in author:
                        # Try to find ORCID
                        orcid = find_orcid_for_author(author.get("name", ""), author.get("email", ""))
                        if orcid:
                            author["@id"] = f"https://orcid.org/{orcid}"

                        authors.append(author)

        return authors if authors else None

    except (json.JSONDecodeError, ValueError):
        return None


def find_orcid_for_author(name: str, email: str = "") -> Optional[str]:
    """
    Attempt to find ORCID identifier for an author.

    This function searches the ORCID registry for an author by name and email.
    Note: This requires internet access and may be rate-limited by ORCID.

    Args:
        name (str): The author's name.
        email (str): The author's email (optional).

    Returns:
        Optional[str]: The ORCID identifier (without URL prefix) or None if not found.
    """
    if not name:
        return None

    try:
        # Search ORCID by name
        search_url = "https://pub.orcid.org/v3.0/search"
        query = f'given-names:"{name.split()[0]}" AND family-name:"{name.split()[-1]}"'

        if email:
            query += f' OR email:"{email}"'

        params = {
            "q": query,
            "rows": 1,
        }

        headers = {
            "Accept": "application/json",
        }

        response = requests.get(search_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get("result") and len(data["result"]) > 0:
            orcid_path = data["result"][0].get("orcid-identifier", {}).get("path")
            if orcid_path:
                return orcid_path

    except Exception:
        # Silently fail - ORCID lookup is optional
        pass

    return None


def get(repository_url: str) -> Dict:
    """
    Extract author information from a GitHub repository.

    This function uses multiple strategies to extract author information:
    1. From GitHub API contributors endpoint
    2. From setup.py author field
    3. From pyproject.toml author field
    4. From package.json author field

    Each author includes name, email (if available), GitHub URL, and ORCID identifier
    (if found in the ORCID registry).

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'author' property and its value.
              Returns an empty dict if no authors can be extracted.

    Example:
        >>> result = get("https://github.com/rsiebes/sshoc-nl-codemeta-generator")
        >>> print(result)
        {'author': [{'name': '...', '@type': 'Person', 'url': '...', '@id': '...'}]}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    authors = None

    # Strategy 1: Try GitHub API (most comprehensive)
    authors = extract_authors_from_github_api(owner, repo)
    if authors:
        return {"author": authors}

    # Strategy 2: Try setup.py
    authors = extract_authors_from_setup_py(owner, repo)
    if authors:
        return {"author": authors}

    # Strategy 3: Try pyproject.toml
    authors = extract_authors_from_pyproject_toml(owner, repo)
    if authors:
        return {"author": authors}

    # Strategy 4: Try package.json
    authors = extract_authors_from_package_json(owner, repo)
    if authors:
        return {"author": authors}

    return {}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/rsiebes/sshoc-nl-codemeta-generator",
        "https://github.com/sodascience/osmenrich",
    ]

    for repo_url in test_repos:
        result = get(repo_url)
        if result:
            print(f"Repository: {repo_url}")
            print(f"Authors: {json.dumps(result, indent=2)}")
            print()
        else:
            print(f"Failed to extract authors from {repo_url}")
