"""
CodeMeta Maintainer Module

This module extracts maintainer information from a GitHub repository.
It identifies active maintainers and contributors responsible for project maintenance.
Includes support for ORCID identifiers for researchers.
"""

from typing import Dict, List, Optional
from src.github_api import (
    parse_repository_url,
    fetch_file_content,
    fetch_repository_info,
    fetch_repository_contributors,
)
import re


def extract_orcid_from_text(text: str) -> Optional[str]:
    """
    Extract ORCID identifier from text.
    
    ORCID format: XXXX-XXXX-XXXX-XXXX
    
    Args:
        text (str): Text to search for ORCID
    
    Returns:
        Optional[str]: ORCID identifier if found
    """
    # ORCID format: XXXX-XXXX-XXXX-XXXX or orcid.org/XXXX-XXXX-XXXX-XXXX
    orcid_match = re.search(r'(?:orcid\.org/)?([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])', text, re.IGNORECASE)
    if orcid_match:
        return orcid_match.group(1)
    return None


def extract_maintainers_from_readme(owner: str, repo: str) -> List[Dict]:
    """
    Extract maintainer information from README.md including ORCID identifiers.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of maintainer objects with ORCID support.
    """
    try:
        maintainers = []
        readme = fetch_file_content(owner, repo, "README.md")
        
        if not readme:
            return maintainers

        # Look for maintainers section
        maintainers_section = re.search(
            r'#+\s*(?:Maintainers?|Core Team)\s*\n(.*?)(?:\n#+|\Z)',
            readme,
            re.IGNORECASE | re.DOTALL
        )
        
        if maintainers_section:
            section_text = maintainers_section.group(1)
            
            # Split by lines to process each maintainer entry
            for line in section_text.split('\n'):
                if not line.strip():
                    continue
                
                # Extract name and email - match name followed by email in parentheses
                name_match = re.search(r'(?:[-*]\s+)?([A-Za-z\s]+?)\s*\(([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\)', line)
                if not name_match:
                    # Try without email
                    name_match = re.search(r'(?:[-*]\s+)?([A-Za-z\s]+?)(?:\s|$)', line)
                if name_match:
                    name = name_match.group(1).strip()
                    email = name_match.group(2) if len(name_match.groups()) > 1 and name_match.group(2) else None
                    
                    if name and len(name) > 2 and not name.lower().startswith('the '):
                        maintainer = {
                            "@type": "Person",
                            "name": name
                        }
                        if email:
                            maintainer["email"] = email
                        
                        # Extract ORCID if present
                        orcid = extract_orcid_from_text(line)
                        if orcid:
                            maintainer["identifier"] = f"https://orcid.org/{orcid}"
                        
                        # Avoid duplicates
                        if not any(m.get("name") == name for m in maintainers):
                            maintainers.append(maintainer)

        return maintainers

    except Exception:
        return []


def extract_maintainers_from_package_files(owner: str, repo: str) -> List[Dict]:
    """
    Extract maintainer information from package files (setup.py, package.json, etc.).
    Includes ORCID identifier extraction.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of maintainer objects.
    """
    try:
        maintainers = []

        # Check setup.py
        setup_py = fetch_file_content(owner, repo, "setup.py")
        if setup_py:
            # Extract maintainer_email and maintainer
            maintainer_match = re.search(r'maintainer\s*=\s*["\']([^"\']+)["\']', setup_py)
            email_match = re.search(r'maintainer_email\s*=\s*["\']([^"\']+)["\']', setup_py)
            
            if maintainer_match or email_match:
                maintainer = {"@type": "Person"}
                
                if maintainer_match:
                    maintainer["name"] = maintainer_match.group(1)
                
                if email_match:
                    maintainer["email"] = email_match.group(1)
                
                # Extract ORCID from entire setup.py
                orcid = extract_orcid_from_text(setup_py)
                if orcid:
                    maintainer["identifier"] = f"https://orcid.org/{orcid}"
                
                if "name" in maintainer or "email" in maintainer:
                    maintainers.append(maintainer)

        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            # Extract maintainers array
            maintainers_match = re.search(r'"maintainers"\s*:\s*\[(.*?)\]', package_json, re.DOTALL)
            if maintainers_match:
                maintainers_text = maintainers_match.group(1)
                
                # Extract individual maintainers
                for match in re.finditer(
                    r'"name"\s*:\s*"([^"]+)"(?:.*?"email"\s*:\s*"([^"]+)")?',
                    maintainers_text,
                    re.DOTALL
                ):
                    name = match.group(1)
                    email = match.group(2) if match.group(2) else None
                    
                    maintainer = {
                        "@type": "Person",
                        "name": name
                    }
                    if email:
                        maintainer["email"] = email
                    
                    # Extract ORCID from maintainer entry
                    orcid = extract_orcid_from_text(match.group(0))
                    if orcid:
                        maintainer["identifier"] = f"https://orcid.org/{orcid}"
                    
                    if not any(m.get("name") == name for m in maintainers):
                        maintainers.append(maintainer)

        # Check pyproject.toml
        pyproject_toml = fetch_file_content(owner, repo, "pyproject.toml")
        if pyproject_toml:
            # Extract maintainers
            maintainers_match = re.search(
                r'maintainers\s*=\s*\[(.*?)\]',
                pyproject_toml,
                re.DOTALL
            )
            if maintainers_match:
                maintainers_text = maintainers_match.group(1)
                
                for match in re.finditer(
                    r'["\']([^"\']+)["\']',
                    maintainers_text
                ):
                    name_or_email = match.group(1)
                    
                    # Check if it's an email
                    if '@' in name_or_email:
                        maintainer = {
                            "@type": "Person",
                            "email": name_or_email
                        }
                    else:
                        maintainer = {
                            "@type": "Person",
                            "name": name_or_email
                        }
                    
                    # Extract ORCID
                    orcid = extract_orcid_from_text(name_or_email)
                    if orcid:
                        maintainer["identifier"] = f"https://orcid.org/{orcid}"
                    
                    if not any(m.get("name") == name_or_email or m.get("email") == name_or_email for m in maintainers):
                        maintainers.append(maintainer)

        return maintainers

    except Exception:
        return []


def extract_maintainers_from_github_api(owner: str, repo: str) -> List[Dict]:
    """
    Extract maintainer information from GitHub API (repository owner and collaborators).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of maintainer objects.
    """
    try:
        maintainers = []

        # Get repository info to identify the owner
        repo_info = fetch_repository_info(owner, repo)
        if repo_info:
            owner_info = repo_info.get("owner", {})
            if owner_info:
                maintainer = {
                    "@type": "Person",
                    "name": owner_info.get("login", owner),
                    "url": owner_info.get("html_url")
                }
                maintainers.append(maintainer)

        # Get contributors (top contributors are likely maintainers)
        contributors = fetch_repository_contributors(owner, repo)
        if contributors:
            # Get top 5 contributors
            for contributor in contributors[:5]:
                if contributor.get("login") != owner:  # Avoid duplicating owner
                    maintainer = {
                        "@type": "Person",
                        "name": contributor.get("login"),
                        "url": contributor.get("html_url"),
                        "contributions": contributor.get("contributions")
                    }
                    maintainers.append(maintainer)

        return maintainers

    except Exception:
        return []


def extract_maintainers_from_contributing(owner: str, repo: str) -> List[Dict]:
    """
    Extract maintainer information from CONTRIBUTING.md including ORCID identifiers.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of maintainer objects.
    """
    try:
        maintainers = []
        
        # Check for CONTRIBUTING.md
        contributing = fetch_file_content(owner, repo, "CONTRIBUTING.md")
        if not contributing:
            contributing = fetch_file_content(owner, repo, ".github/CONTRIBUTING.md")
        
        if not contributing:
            return maintainers

        # Look for maintainers or contact section
        contact_section = re.search(
            r'#+\s*(?:Contact|Maintainers?|Questions|Support)\s*\n(.*?)(?:\n#+|\Z)',
            contributing,
            re.IGNORECASE | re.DOTALL
        )
        
        if contact_section:
            section_text = contact_section.group(1)
            
            # Extract emails and names
            for line in section_text.split('\n'):
                if not line.strip():
                    continue
                
                # Try to match name with email in angle brackets
                name_match = re.search(
                    r'(?:[-*]\s+)?([A-Za-z\s]+?)\s*<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>',
                    line
                )
                if not name_match:
                    # Try to match just name
                    name_match = re.search(
                        r'(?:[-*]\s+)?([A-Za-z\s]+?)(?:\s|$)',
                        line
                    )
                if name_match:
                    name = name_match.group(1).strip()
                    email = name_match.group(2) if len(name_match.groups()) > 1 and name_match.group(2) else None
                    
                    if name and len(name) > 2 and not name.lower().startswith('the '):
                        maintainer = {
                            "@type": "Person",
                            "name": name
                        }
                        if email:
                            maintainer["email"] = email
                        
                        # Extract ORCID if present
                        orcid = extract_orcid_from_text(line)
                        if orcid:
                            maintainer["identifier"] = f"https://orcid.org/{orcid}"
                        
                        if not any(m.get("name") == name for m in maintainers):
                            maintainers.append(maintainer)

        return maintainers

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract maintainer information from a GitHub repository.
    Includes ORCID identifiers for researchers.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'maintainer' key containing Person objects with ORCID support.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    # Extract maintainers from multiple sources
    all_maintainers = []
    seen_names = set()

    # Extract from README
    readme_maintainers = extract_maintainers_from_readme(owner, repo)
    for maintainer in readme_maintainers:
        name = maintainer.get("name")
        if name and name not in seen_names:
            all_maintainers.append(maintainer)
            seen_names.add(name)

    # Extract from package files
    package_maintainers = extract_maintainers_from_package_files(owner, repo)
    for maintainer in package_maintainers:
        name = maintainer.get("name")
        if name and name not in seen_names:
            all_maintainers.append(maintainer)
            seen_names.add(name)

    # Extract from CONTRIBUTING.md
    contributing_maintainers = extract_maintainers_from_contributing(owner, repo)
    for maintainer in contributing_maintainers:
        name = maintainer.get("name")
        if name and name not in seen_names:
            all_maintainers.append(maintainer)
            seen_names.add(name)

    # Extract from GitHub API
    api_maintainers = extract_maintainers_from_github_api(owner, repo)
    for maintainer in api_maintainers:
        name = maintainer.get("name")
        if name and name not in seen_names:
            all_maintainers.append(maintainer)
            seen_names.add(name)

    if not all_maintainers:
        return {}

    # Sort by name
    all_maintainers.sort(key=lambda x: x.get("name", ""))

    # Return as array (CodeMeta allows array of maintainers)
    return {
        "maintainer": all_maintainers
    }
