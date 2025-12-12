#!/usr/bin/env python3
"""
CodeMeta property module for extracting contributors from a GitHub repository.

This module extracts contributor information using multiple strategies:
1. From GitHub API contributors endpoint (most reliable)
2. From configuration files (CONTRIBUTORS, AUTHORS, etc.)
3. From commit history (alternative source)

The module returns a list of contributors with their details including name, email,
GitHub URL, affiliation, and ORCID identifier when available.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List
import requests
import re

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, get_github_token
from src.utils import normalize_url
from src.modules.codemeta_author import find_orcid_for_author


def fetch_contributors_from_api(owner: str, repo: str, limit: int = 100) -> List[Dict]:
    """
    Fetch contributors from GitHub API.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        limit (int): Maximum number of contributors to fetch (default: 100).

    Returns:
        List[Dict]: A list of contributor dictionaries with name, URL, and contributions.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        # Fetch contributors
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
            params={"per_page": min(limit, 100), "anon": "true"}
        )

        if response.status_code == 200:
            contributors_data = response.json()
            contributors = []

            for contrib in contributors_data:
                if isinstance(contrib, dict):
                    # Skip anonymous contributors
                    if contrib.get("login") == "anonymous":
                        continue

                    contributor = {
                        "name": contrib.get("login", ""),
                        "url": contrib.get("html_url", ""),
                        "@type": "Person",
                        "contributions": contrib.get("contributions", 0),
                    }

                    # Try to get additional information from user profile
                    if contrib.get("type") == "User":
                        user_url = contrib.get("url")
                        if user_url:
                            try:
                                user_response = requests.get(
                                    user_url,
                                    headers=headers,
                                    timeout=10
                                )
                                if user_response.status_code == 200:
                                    user_data = user_response.json()
                                    if user_data.get("name"):
                                        contributor["name"] = user_data.get("name")
                                    if user_data.get("email"):
                                        contributor["email"] = user_data.get("email")
                                    if user_data.get("company"):
                                        contributor["affiliation"] = user_data.get("company")
                            except Exception:
                                pass

                    contributors.append(contributor)

            return contributors[:limit]

        return []

    except Exception:
        return []


def fetch_contributors_from_file(owner: str, repo: str) -> List[Dict]:
    """
    Fetch contributors from CONTRIBUTORS or AUTHORS file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        List[Dict]: A list of contributor dictionaries parsed from the file.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        # Try different file names
        file_names = ["CONTRIBUTORS", "CONTRIBUTORS.md", "AUTHORS", "AUTHORS.md", "CONTRIBUTORS.txt"]

        for file_name in file_names:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_name}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                file_data = response.json()
                if "content" in file_data:
                    import base64
                    content = base64.b64decode(file_data["content"]).decode("utf-8")

                    # Parse contributors from file
                    contributors = []
                    lines = content.split("\n")

                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue

                        # Try to parse name and email from line
                        # Formats: "Name", "Name <email>", "Name (email)", "Name - email"
                        match = re.match(r"^([^<(\-]+?)(?:\s*<([^>]+)>|\s*\(([^)]+)\)|\s*-\s*(.+))?$", line)
                        if match:
                            name = match.group(1).strip()
                            email = match.group(2) or match.group(3) or match.group(4)
                            if email:
                                email = email.strip()

                            if name:
                                contributor = {
                                    "name": name,
                                    "@type": "Person",
                                }
                                if email and "@" in email:
                                    contributor["email"] = email
                                contributors.append(contributor)

                    return contributors

        return []

    except Exception:
        return []


def enrich_contributors_with_orcid(contributors: List[Dict]) -> List[Dict]:
    """
    Enrich contributor list with ORCID identifiers.

    Args:
        contributors (List[Dict]): List of contributors to enrich.

    Returns:
        List[Dict]: List of contributors with ORCID identifiers added.
    """
    enriched = []

    for contributor in contributors:
        name = contributor.get("name", "")
        email = contributor.get("email", "")

        # Try to find ORCID for this contributor
        orcid = find_orcid_for_author(name, email)
        if orcid:
            contributor["@id"] = f"https://orcid.org/{orcid}"

        enriched.append(contributor)

    return enriched


def remove_duplicate_contributors(contributors: List[Dict]) -> List[Dict]:
    """
    Remove duplicate contributors from the list.

    Args:
        contributors (List[Dict]): List of contributors.

    Returns:
        List[Dict]: List with duplicates removed (based on name and URL).
    """
    seen = set()
    unique = []

    for contributor in contributors:
        # Create a unique key based on name and URL
        name = contributor.get("name", "").lower()
        url = contributor.get("url", "").lower()
        key = (name, url)

        if key not in seen:
            seen.add(key)
            unique.append(contributor)

    return unique


def get(repository_url: str) -> Dict:
    """
    Extract contributors from a GitHub repository.

    This function uses multiple strategies to extract contributor information:
    1. From GitHub API contributors endpoint (most reliable)
    2. From CONTRIBUTORS/AUTHORS files
    3. Enriches with ORCID identifiers when available

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'contributor' property with a list of contributors.
              Returns an empty dict if no contributors can be extracted.

    Example:
        >>> result = get("https://github.com/tensorflow/tensorflow")
        >>> print(result)
        {'contributor': [
            {'name': 'Contributor 1', '@type': 'Person', 'url': '...'},
            {'name': 'Contributor 2', '@type': 'Person', 'url': '...'},
        ]}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    contributors = []

    # Strategy 1: Try GitHub API (most reliable)
    contributors = fetch_contributors_from_api(owner, repo, limit=50)

    # Strategy 2: Try CONTRIBUTORS/AUTHORS files (if API returns nothing)
    if not contributors:
        contributors = fetch_contributors_from_file(owner, repo)

    if not contributors:
        return {}

    # Remove duplicates
    contributors = remove_duplicate_contributors(contributors)

    # Enrich with ORCID identifiers
    contributors = enrich_contributors_with_orcid(contributors)

    # Remove the contributions count field (not part of CodeMeta)
    for contributor in contributors:
        contributor.pop("contributions", None)

    return {"contributor": contributors}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/tensorflow/tensorflow",
        "https://github.com/openai/gpt-2",
        "https://github.com/rust-lang/rust",
    ]

    for repo_url in test_repos:
        print(f"\nTesting: {repo_url}")
        result = get(repo_url)
        if result and "contributor" in result:
            contributors = result["contributor"]
            print(f"Contributors found: {len(contributors)}")
            for contrib in contributors[:3]:
                print(f"  - {contrib.get('name', 'N/A')}")
        else:
            print("No contributors found")
