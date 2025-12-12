"""
CodeMeta Maintainer Module

This module extracts maintainer information from a GitHub repository.
Includes support for ORCID (Open Researcher and Contributor ID) identifiers.
"""

from typing import Dict, List, Optional
from src.github_api import (
    parse_repository_url,
    fetch_file_content,
    fetch_repository_info,
    fetch_repository_contributors,
)
import re


# Common false positives to filter out
COMMON_FALSE_POSITIVES = {
    'the', 'not', 'that', 'stack', 'instead', 'and', 'or', 'is', 'are', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'this', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'only', 'same', 'so', 'than', 'too',
    'very', 'just', 'also', 'as', 'if', 'in', 'on', 'at', 'by', 'for', 'from',
    'of', 'to', 'with', 'up', 'out', 'off', 'over', 'under', 'above', 'below',
    'between', 'through', 'during', 'before', 'after', 'page', 'line', 'section',
    'part', 'text', 'content', 'data', 'value', 'item', 'element', 'object',
    'type', 'class', 'method', 'function', 'variable', 'parameter', 'argument',
    'result', 'return', 'error', 'exception', 'warning', 'message', 'log',
    'debug', 'info', 'trace', 'level', 'mode', 'state', 'status', 'flag',
    'option', 'setting', 'config', 'configuration', 'a', 'an', 'as', 'at'
}


def is_valid_name(name: str) -> bool:
    """
    Validate if a name is likely a real person name.
    
    Args:
        name (str): Name to validate
        
    Returns:
        bool: True if name appears to be valid
    """
    if not name or len(name) < 3:
        return False
    
    # Check if it's a common false positive
    if name.lower() in COMMON_FALSE_POSITIVES:
        return False
    
    # Names should either have a space (first and last name) or be a known GitHub username
    # GitHub usernames are typically lowercase alphanumeric with hyphens/underscores
    if ' ' in name:
        # Multi-word name - check it's not just articles/prepositions
        parts = name.split()
        if len(parts) < 2:
            return False
        # At least 2 parts and not starting with 'the'
        if name.lower().startswith('the '):
            return False
        return True
    else:
        # Single word - could be a GitHub username
        # GitHub usernames are typically 1-39 characters, alphanumeric, hyphens, underscores
        if re.match(r'^[a-zA-Z0-9_-]{2,39}$', name):
            return True
        return False


def extract_orcid_from_text(text: str) -> Optional[str]:
    """
    Extract ORCID identifier from text.

    Args:
        text (str): Text to search for ORCID

    Returns:
        Optional[str]: ORCID identifier in format XXXX-XXXX-XXXX-XXXX if found
    """
    # Match ORCID URLs or plain ORCID format
    orcid_pattern = r'(?:orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])'
    match = re.search(orcid_pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1)
    
    return None


def extract_maintainers_from_readme(owner: str, repo: str) -> List[Dict]:
    """
    Extract maintainer information from README.md including ORCID identifiers.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        List[Dict]: List of maintainer objects.
    """
    try:
        maintainers = []
        
        # Fetch README
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
                    
                    if is_valid_name(name):
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
    Extract maintainer information from package files (setup.py, package.json, pyproject.toml).

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
            # Extract maintainer field
            maintainer_match = re.search(r'maintainer\s*=\s*["\']([^"\']+)["\']', setup_py)
            if maintainer_match:
                name = maintainer_match.group(1).strip()
                if is_valid_name(name):
                    maintainer = {
                        "@type": "Person",
                        "name": name
                    }
                    
                    # Extract email
                    email_match = re.search(r'maintainer_email\s*=\s*["\']([^"\']+)["\']', setup_py)
                    if email_match:
                        maintainer["email"] = email_match.group(1).strip()
                    
                    maintainers.append(maintainer)
        
        # Check package.json
        package_json = fetch_file_content(owner, repo, "package.json")
        if package_json:
            # Extract maintainers array
            maintainers_match = re.search(r'"maintainers"\s*:\s*\[(.*?)\]', package_json, re.DOTALL)
            if maintainers_match:
                maintainers_text = maintainers_match.group(1)
                # Extract individual maintainer objects
                for obj_match in re.finditer(r'\{\s*"name"\s*:\s*"([^"]+)"(?:,\s*"email"\s*:\s*"([^"]+)")?\s*\}', maintainers_text):
                    name = obj_match.group(1).strip()
                    if is_valid_name(name):
                        maintainer = {
                            "@type": "Person",
                            "name": name
                        }
                        if obj_match.group(2):
                            maintainer["email"] = obj_match.group(2).strip()
                        
                        if not any(m.get("name") == name for m in maintainers):
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
                    
                    if is_valid_name(name):
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


def extract_maintainers_from_github_api(owner: str, repo: str) -> List[Dict]:
    """
    Extract maintainer information from GitHub API (repository owner and top contributors).

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
                        "name": contributor.get("login", ""),
                        "url": contributor.get("html_url"),
                        "contributions": contributor.get("contributions")
                    }
                    maintainers.append(maintainer)

        return maintainers

    except Exception:
        return []


def get(repository_url: str) -> Dict:
    """
    Extract maintainer information from a GitHub repository.

    Args:
        repository_url (str): The GitHub repository URL.

    Returns:
        Dict: Dictionary with 'maintainer' key containing array of Person objects if found.
    """
    owner, repo = parse_repository_url(repository_url)
    if not owner or not repo:
        return {}

    maintainers = []

    # Extract from different sources in priority order
    # 1. README.md
    maintainers.extend(extract_maintainers_from_readme(owner, repo))
    
    # 2. Package files
    maintainers.extend(extract_maintainers_from_package_files(owner, repo))
    
    # 3. CONTRIBUTING.md
    maintainers.extend(extract_maintainers_from_contributing(owner, repo))
    
    # 4. GitHub API (owner and top contributors)
    maintainers.extend(extract_maintainers_from_github_api(owner, repo))

    if not maintainers:
        return {}

    # Remove duplicates by name
    seen_names = set()
    unique_maintainers = []
    for m in maintainers:
        name = m.get("name")
        if name and name not in seen_names:
            seen_names.add(name)
            unique_maintainers.append(m)

    # Sort by name
    unique_maintainers.sort(key=lambda x: x.get("name", "").lower())

    return {
        "maintainer": unique_maintainers
    }
