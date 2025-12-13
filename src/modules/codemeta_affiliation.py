"""
CodeMeta affiliation Module

Extracts organizational affiliations according to CodeMeta 3.1 standard.
The affiliation property describes the organization(s) with which the software
or its creators/maintainers are affiliated.

This module extracts affiliations from:
1. Author/maintainer profiles (GitHub user bio, company field)
2. Repository organization
3. README file mentions
4. GitHub API organization field

Returns:
    str: Single affiliation string (e.g., "MIT", "Google")
    list: Multiple affiliations if applicable
    None: If no affiliation can be determined
"""

import logging
import re
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)


class AffiliationExtractor:
    """Extracts affiliations from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the AffiliationExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.owner = repo_data.get("owner", {})
        self.organization = repo_data.get("organization")
        self.owner_type = self.owner.get("type", "")  # "User" or "Organization"

    def extract(self) -> Optional[Union[str, List[str]]]:
        """
        Extract affiliations from repository metadata.

        Returns:
            str: Single affiliation
            list: Multiple affiliations if applicable
            None: If no affiliation can be determined
        """
        affiliations = []

        # Check if owner is an organization
        if self.owner_type == "Organization":
            org_name = self.owner.get("login", "")
            if org_name:
                affiliations.append(org_name)
                logger.info(f"Found organization affiliation: {org_name}")

        # Check for organization field
        if self.organization:
            org_name = self.organization.get("login") or self.organization.get("name")
            if org_name and org_name not in affiliations:
                affiliations.append(org_name)
                logger.info(f"Found organization affiliation: {org_name}")

        # Check owner company field (if owner is a user)
        if self.owner_type == "User":
            company = self.owner.get("company")
            if company and company.strip():
                # Clean up company name (remove @ symbols, extra whitespace)
                company = company.strip().lstrip("@").strip()
                if company and company not in affiliations:
                    affiliations.append(company)
                    logger.info(f"Found company affiliation: {company}")

        # Return results
        if len(affiliations) == 0:
            logger.debug("No affiliations found")
            return None
        elif len(affiliations) == 1:
            return affiliations[0]
        else:
            return affiliations

    def _clean_affiliation_name(self, name: str) -> str:
        """
        Clean and normalize affiliation name.

        Args:
            name: Raw affiliation name

        Returns:
            str: Cleaned affiliation name
        """
        # Remove @ symbols
        name = name.lstrip("@").strip()
        
        # Remove common prefixes/suffixes
        name = re.sub(r"^(the|The)\s+", "", name)
        name = re.sub(r"\s+(Inc|Inc\.|Ltd|Ltd\.|LLC|Corp|Corporation)$", "", name)
        
        return name.strip()


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[Union[str, List[str]]]:
    """
    Extract affiliations from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Single affiliation
        list: Multiple affiliations if applicable
        None: If no affiliation can be determined
    """
    try:
        extractor = AffiliationExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted affiliation(s): {result}")
            return result
        else:
            logger.debug("No affiliations found with sufficient data")
            return None

    except Exception as e:
        logger.error(f"Error extracting affiliation: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[Union[str, List[str]]]]:
    """
    Extract affiliation from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'affiliation' property and its value.
              Returns an empty dict if no affiliation can be extracted.
    """
    try:
        from src.github_api import parse_repository_url, fetch_repository_info
        from src.utils import normalize_url

        repository_url = normalize_url(repository_url)
        owner, repo = parse_repository_url(repository_url)
        if not owner or not repo:
            return {}

        repo_data = fetch_repository_info(owner, repo)
        if not repo_data:
            return {}

        result = extract(repo_data)

        if result:
            return {"affiliation": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
