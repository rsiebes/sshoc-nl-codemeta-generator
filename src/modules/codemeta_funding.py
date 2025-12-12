#!/usr/bin/env python3
"""
CodeMeta property module for extracting funding information from a GitHub repository.

This module extracts funding information using multiple strategies:
1. From FUNDING.yml file (GitHub's native funding configuration)
2. From README.md file (text-based funding information)
3. From FUNDING, SPONSORS, or SUPPORT files
4. From package.json funding field

The module returns a list of funding sources with details including type, URL, and description.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List
import requests
import re
import base64

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.github_api import parse_repository_url, get_github_token
from src.utils import normalize_url


def is_valid_funding_url(url: str) -> bool:
    """
    Validate that a URL is a legitimate funding URL.
    
    Only accepts URLs from known funding platforms or URLs that clearly indicate funding.
    
    Args:
        url (str): The URL to validate.
        
    Returns:
        bool: True if the URL is a valid funding URL, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    
    # Must start with http
    if not url_lower.startswith("http"):
        return False
    
    # Must not be too short (avoid fragments)
    if len(url) < 15:
        return False
    
    # Known funding platforms
    valid_domains = [
        "patreon.com",
        "ko-fi.com",
        "liberapay.com",
        "buymeacoffee.com",
        "github.com/sponsors",
        "tidelift.com",
        "issuehunt.io",
        "otechie.com",
        "opencollective.com",
        "gumroad.com",
        "stripe.com",
        "paypal.com",
        "donate",
        "sponsor",
        "funding",
    ]
    
    # Check if URL contains any known funding platform
    for domain in valid_domains:
        if domain in url_lower:
            return True
    
    return False


def fetch_funding_yml(owner: str, repo: str) -> List[Dict]:
    """
    Fetch funding information from .github/FUNDING.yml file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        List[Dict]: A list of funding sources from FUNDING.yml.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/.github/FUNDING.yml"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            file_data = response.json()
            if "content" in file_data:
                content = base64.b64decode(file_data["content"]).decode("utf-8")

                funding_sources = []
                lines = content.split("\n")

                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse YAML-like format: key: value
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip().strip("'\"")

                        if value:
                            # Map funding types to CodeMeta format
                            funding_type_map = {
                                "github": "GitHub Sponsors",
                                "patreon": "Patreon",
                                "ko_fi": "Ko-fi",
                                "tidelift": "Tidelift",
                                "custom": "Custom",
                                "liberapay": "Liberapay",
                                "issuehunt": "IssueHunt",
                                "otechie": "Otechie",
                                "buymeacoffee": "Buy Me a Coffee",
                                "opencollective": "Open Collective",
                            }

                            funding_type = funding_type_map.get(key, key.replace("_", " ").title())

                            # Handle list values (e.g., github: [user1, user2])
                            if isinstance(value, str) and value.startswith("["):
                                # Parse list format
                                values = re.findall(r"[\w\-]+", value)
                                for v in values:
                                    if key in ["github", "patreon", "ko_fi", "liberapay", "buymeacoffee"]:
                                        url_map = {
                                            "github": "https://github.com/sponsors/{}",
                                            "patreon": "https://patreon.com/{}",
                                            "ko_fi": "https://ko-fi.com/{}",
                                            "liberapay": "https://liberapay.com/{}",
                                            "buymeacoffee": "https://buymeacoffee.com/{}",
                                        }
                                        if key in url_map:
                                            funding_url = url_map[key].format(v)
                                            if is_valid_funding_url(funding_url):
                                                funding_sources.append({
                                                    "type": funding_type,
                                                    "url": funding_url,
                                                })
                            else:
                                # Single value
                                if key in ["github", "patreon", "ko_fi", "liberapay", "buymeacoffee"]:
                                    # These are usernames, construct URLs
                                    url_map = {
                                        "github": "https://github.com/sponsors/{}",
                                        "patreon": "https://patreon.com/{}",
                                        "ko_fi": "https://ko-fi.com/{}",
                                        "liberapay": "https://liberapay.com/{}",
                                        "buymeacoffee": "https://buymeacoffee.com/{}",
                                    }
                                    if key in url_map:
                                        funding_url = url_map[key].format(value)
                                    else:
                                        funding_url = value
                                else:
                                    funding_url = value

                                if is_valid_funding_url(funding_url):
                                    funding_sources.append({
                                        "type": funding_type,
                                        "url": funding_url,
                                    })

                return funding_sources

        return []

    except Exception:
        return []


def fetch_funding_from_readme(owner: str, repo: str) -> List[Dict]:
    """
    Fetch funding information from README.md file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        List[Dict]: A list of funding sources extracted from README.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            file_data = response.json()
            if "content" in file_data:
                content = base64.b64decode(file_data["content"]).decode("utf-8")

                funding_sources = []

                # Look for funding-related sections
                # Must have explicit "Funding" or "Sponsor" heading
                if re.search(r"##\s*(?:Funding|Sponsor|Support|Donate)", content, re.IGNORECASE):
                    # Extract URLs from the section
                    url_pattern = r"https?://[^\s\)>\]]*"
                    urls = re.findall(url_pattern, content)

                    for url_match in urls:
                        # Strict validation: only accept known funding platforms
                        if is_valid_funding_url(url_match):
                            # Determine funding type from URL
                            if "patreon" in url_match.lower():
                                funding_type = "Patreon"
                            elif "ko-fi" in url_match.lower():
                                funding_type = "Ko-fi"
                            elif "liberapay" in url_match.lower():
                                funding_type = "Liberapay"
                            elif "buymeacoffee" in url_match.lower():
                                funding_type = "Buy Me a Coffee"
                            elif "github" in url_match.lower() and "sponsor" in url_match.lower():
                                funding_type = "GitHub Sponsors"
                            elif "opencollective" in url_match.lower():
                                funding_type = "Open Collective"
                            else:
                                funding_type = "Funding"

                            funding_sources.append({
                                "type": funding_type,
                                "url": url_match,
                            })

                return funding_sources

        return []

    except Exception:
        return []


def fetch_funding_from_file(owner: str, repo: str) -> List[Dict]:
    """
    Fetch funding information from dedicated funding files.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        List[Dict]: A list of funding sources from dedicated files.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        # Try different file names
        file_names = ["FUNDING", "FUNDING.md", "SPONSORS", "SPONSORS.md", "SUPPORT", "SUPPORT.md"]

        for file_name in file_names:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_name}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                file_data = response.json()
                if "content" in file_data:
                    content = base64.b64decode(file_data["content"]).decode("utf-8")

                    funding_sources = []

                    # Extract URLs and funding information
                    url_pattern = r"https?://[^\s\)>\]]*"
                    urls = re.findall(url_pattern, content)

                    for url_match in urls:
                        # Strict validation
                        if is_valid_funding_url(url_match):
                            # Determine funding type from URL
                            if "patreon" in url_match.lower():
                                funding_type = "Patreon"
                            elif "ko-fi" in url_match.lower():
                                funding_type = "Ko-fi"
                            elif "liberapay" in url_match.lower():
                                funding_type = "Liberapay"
                            elif "buymeacoffee" in url_match.lower():
                                funding_type = "Buy Me a Coffee"
                            elif "github" in url_match.lower() and "sponsor" in url_match.lower():
                                funding_type = "GitHub Sponsors"
                            elif "opencollective" in url_match.lower():
                                funding_type = "Open Collective"
                            else:
                                funding_type = "Funding"

                            funding_sources.append({
                                "type": funding_type,
                                "url": url_match,
                            })

                    return funding_sources

        return []

    except Exception:
        return []


def fetch_funding_from_package_json(owner: str, repo: str) -> List[Dict]:
    """
    Fetch funding information from package.json file.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.

    Returns:
        List[Dict]: A list of funding sources from package.json.
    """
    try:
        token = get_github_token()
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/package.json"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            file_data = response.json()
            if "content" in file_data:
                content = base64.b64decode(file_data["content"]).decode("utf-8")

                try:
                    import json
                    package_data = json.loads(content)

                    funding_sources = []

                    if "funding" in package_data:
                        funding = package_data["funding"]

                        if isinstance(funding, str):
                            # Single funding URL
                            if is_valid_funding_url(funding):
                                funding_sources.append({
                                    "type": "Funding",
                                    "url": funding,
                                })
                        elif isinstance(funding, dict):
                            # Funding object with type and url
                            funding_type = funding.get("type", "Funding").title()
                            funding_url = funding.get("url", "")
                            if funding_url and is_valid_funding_url(funding_url):
                                funding_sources.append({
                                    "type": funding_type,
                                    "url": funding_url,
                                })
                        elif isinstance(funding, list):
                            # List of funding sources
                            for fund in funding:
                                if isinstance(fund, dict):
                                    funding_type = fund.get("type", "Funding").title()
                                    funding_url = fund.get("url", "")
                                    if funding_url and is_valid_funding_url(funding_url):
                                        funding_sources.append({
                                            "type": funding_type,
                                            "url": funding_url,
                                        })
                                elif isinstance(fund, str):
                                    if is_valid_funding_url(fund):
                                        funding_sources.append({
                                            "type": "Funding",
                                            "url": fund,
                                        })

                    return funding_sources

                except Exception:
                    return []

        return []

    except Exception:
        return []


def remove_duplicate_funding(funding_sources: List[Dict]) -> List[Dict]:
    """
    Remove duplicate funding sources from the list.

    Args:
        funding_sources (List[Dict]): List of funding sources.

    Returns:
        List[Dict]: List with duplicates removed (based on URL).
    """
    seen = set()
    unique = []

    for source in funding_sources:
        url = source.get("url", "").lower()

        if url and url not in seen:
            seen.add(url)
            unique.append(source)

    return unique


def get(repository_url: str) -> Dict:
    """
    Extract funding information from a GitHub repository.

    This function uses multiple strategies to extract funding information:
    1. From .github/FUNDING.yml file (GitHub's native funding configuration)
    2. From README.md file (text-based funding information)
    3. From dedicated FUNDING/SPONSORS/SUPPORT files
    4. From package.json funding field

    Only valid funding URLs from known platforms are included.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'funder' property with a list of funding sources.
              Returns an empty dict if no funding information can be extracted.

    Example:
        >>> result = get("https://github.com/tensorflow/tensorflow")
        >>> print(result)
        {'funder': [
            {'type': 'GitHub Sponsors', 'url': 'https://github.com/sponsors/...'},
            {'type': 'Patreon', 'url': 'https://patreon.com/...'},
        ]}
    """
    repository_url = normalize_url(repository_url)
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    funding_sources = []

    # Strategy 1: Try FUNDING.yml (most reliable)
    funding_sources.extend(fetch_funding_yml(owner, repo))

    # Strategy 2: Try README.md
    if not funding_sources:
        funding_sources.extend(fetch_funding_from_readme(owner, repo))

    # Strategy 3: Try dedicated funding files
    if not funding_sources:
        funding_sources.extend(fetch_funding_from_file(owner, repo))

    # Strategy 4: Try package.json
    if not funding_sources:
        funding_sources.extend(fetch_funding_from_package_json(owner, repo))

    if not funding_sources:
        return {}

    # Remove duplicates
    funding_sources = remove_duplicate_funding(funding_sources)

    return {"funder": funding_sources}


if __name__ == "__main__":
    test_repos = [
        "https://github.com/tensorflow/tensorflow",
        "https://github.com/rust-lang/rust",
        "https://github.com/vuejs/vue",
    ]

    for repo_url in test_repos:
        print(f"\nTesting: {repo_url}")
        result = get(repo_url)
        if result and "funder" in result:
            funders = result["funder"]
            print(f"Funding sources found: {len(funders)}")
            for funder in funders:
                print(f"  - {funder.get('type', 'N/A')}: {funder.get('url', 'N/A')}")
        else:
            print("No funding information found")
