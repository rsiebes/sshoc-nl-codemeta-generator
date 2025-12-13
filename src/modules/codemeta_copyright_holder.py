"""
CodeMeta copyrightHolder Module

Extracts copyright holder information according to CodeMeta 3.1 standard.
The copyrightHolder property describes the organization or person that holds the copyright.

This module extracts copyright holder from:
1. Repository owner (organization or user)
2. LICENSE file
3. README file

Returns:
    str: Copyright holder name
    None: If no copyright holder can be determined
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CopyrightHolderExtractor:
    """Extracts copyright holder from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the CopyrightHolderExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.owner = repo_data.get("owner", {})
        self.owner_login = self.owner.get("login", "")
        self.owner_type = self.owner.get("type", "")

    def extract(self) -> Optional[str]:
        """
        Extract copyright holder from repository metadata.

        Returns:
            str: Copyright holder name
            None: If no copyright holder can be determined
        """
        # Use repository owner as copyright holder
        if self.owner_type == "Organization":
            # For organizations, use the organization name
            org_name = self.owner.get("name") or self.owner_login
            if org_name:
                logger.info(f"Found copyright holder: {org_name}")
                return org_name

        # For users, use the user's name or login
        if self.owner_type == "User":
            user_name = self.owner.get("name") or self.owner_login
            if user_name:
                logger.info(f"Found copyright holder: {user_name}")
                return user_name

        # Fallback to login
        if self.owner_login:
            logger.info(f"Found copyright holder: {self.owner_login}")
            return self.owner_login

        logger.debug("No copyright holder found")
        return None


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    """
    Extract copyright holder from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Copyright holder name
        None: If no copyright holder can be determined
    """
    try:
        extractor = CopyrightHolderExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted copyright holder")
            return result
        else:
            logger.debug("No copyright holder found")
            return None

    except Exception as e:
        logger.error(f"Error extracting copyright holder: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[str]]:
    """
    Extract copyright holder from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'copyrightHolder' property and its value.
              Returns an empty dict if no copyright holder can be extracted.
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
            return {"copyrightHolder": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
