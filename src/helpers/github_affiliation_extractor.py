"""Extract affiliation information from GitHub user profiles."""

import os
import re
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

from src.core import get_logger

logger = get_logger(__name__)
load_dotenv()


def get_github_user_profile(github_login: str) -> Optional[Dict[str, Any]]:
    """
    Fetch GitHub user profile data.

    Args:
        github_login: GitHub username/login

    Returns:
        Dictionary with user profile data, or None if fetch fails
    """
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'

        url = f'https://api.github.com/users/{github_login}'
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to fetch GitHub profile for {github_login}: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error fetching GitHub profile for {github_login}: {str(e)}")
        return None


def parse_company_field(company_str: str) -> str:
    """
    Parse the company field from GitHub profile.

    Handles various formats like:
    - "University of Amsterdam"
    - "@motherduckdb" (remove @)
    - "Assistant professor @UtrechtUniversity" (extract organization)
    - "VU" (abbreviation)

    Args:
        company_str: Raw company string from GitHub profile

    Returns:
        Cleaned organization name
    """
    if not company_str:
        return ""

    cleaned = company_str.strip()

    # Handle @ symbols - extract organization name
    if '@' in cleaned:
        # Take the part after @
        parts = cleaned.split('@')
        org_part = parts[-1].strip()
        cleaned = org_part
    else:
        # Extract organization from "Title Organization" format
        if any(word in cleaned.lower() for word in ['professor', 'researcher', 'engineer', 'scientist', 'assistant', 'associate']):
            # Try to extract organization after title
            parts = cleaned.split()
            # Find parts that look like organization names (capitalized, longer than 2 chars)
            org_parts = [p for p in parts if len(p) > 2 and p[0].isupper()]
            if org_parts:
                cleaned = ' '.join(org_parts)

    # Handle CamelCase organization names (e.g., "UtrechtUniversity" -> "Utrecht University")
    cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)

    # Expand common abbreviations
    abbreviations = {
        'VU': 'Vrije Universiteit Amsterdam',
        'UvA': 'University of Amsterdam',
        'UU': 'Utrecht University',
        'TU': 'Delft University of Technology',
        'RUG': 'University of Groningen',
    }

    for abbr, full_name in abbreviations.items():
        if cleaned.strip() == abbr:
            cleaned = full_name
            break

    return cleaned.strip()


def extract_affiliation_from_github(github_login: str) -> Optional[Dict[str, str]]:
    """
    Extract affiliation information from GitHub user profile.

    Args:
        github_login: GitHub username/login

    Returns:
        Dictionary with 'name' and 'url' keys, or None if not found
    """
    try:
        # Fetch GitHub user profile
        profile = get_github_user_profile(github_login)
        if not profile:
            logger.warning(f"Could not fetch profile for {github_login}")
            return None

        company = profile.get('company')
        if not company:
            logger.debug(f"No company information in GitHub profile for {github_login}")
            return None

        # Parse the company field
        organization_name = parse_company_field(company)
        if not organization_name:
            logger.debug(f"Could not parse organization from company field: {company}")
            return None

        logger.debug(f"Extracted organization for {github_login}: {organization_name}")

        return {
            'name': organization_name,
            'github_login': github_login,
            'raw_company': company
        }

    except Exception as e:
        logger.error(f"Error extracting affiliation for {github_login}: {str(e)}")
        return None


def extract_affiliations_from_authors(authors_json: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Extract affiliations for multiple authors from their GitHub profiles.

    Args:
        authors_json: JSON string with authors data (from extract_unique_authors)

    Returns:
        Dictionary mapping author names to affiliation data
    """
    import json

    try:
        authors_data = json.loads(authors_json)
        authors = authors_data.get('authors', [])

        affiliations = {}

        for author in authors:
            name = author.get('name')
            login = author.get('login')

            if not name or not login:
                continue

            # Extract affiliation from GitHub profile
            affiliation = extract_affiliation_from_github(login)
            affiliations[name] = affiliation

        return affiliations

    except Exception as e:
        logger.error(f"Error extracting affiliations: {str(e)}")
        return {}


if __name__ == '__main__':
    # Test the functions
    import sys
    sys.path.insert(0, '.')

    print("Testing GitHub affiliation extraction...\n")

    # Test with known GitHub users
    test_users = ['jrvosse', 'nichtich', 'leonardovida', 'J535D165', 'vankesteren']

    for login in test_users:
        print(f"User: {login}")
        affiliation = extract_affiliation_from_github(login)
        if affiliation:
            print(f"  Organization: {affiliation['name']}")
            print(f"  Raw: {affiliation['raw_company']}")
        else:
            print(f"  No affiliation found")
        print()
