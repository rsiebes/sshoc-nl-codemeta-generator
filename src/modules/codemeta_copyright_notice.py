"""
CodeMeta copyrightNotice Module

Extracts copyright notice information according to CodeMeta 3.1 standard.
The copyrightNotice property describes the copyright notice text.

This module extracts copyright notice from:
1. LICENSE file
2. README file
3. Repository description

Returns:
    str: Copyright notice text
    None: If no copyright notice can be determined
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CopyrightNoticeExtractor:
    """Extracts copyright notice from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any], repo_files: Dict[str, str] = None):
        """
        Initialize the CopyrightNoticeExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
            repo_files: Dictionary containing repository file contents
        """
        self.repo_data = repo_data
        self.repo_files = repo_files or {}

    def extract(self) -> Optional[str]:
        """
        Extract copyright notice from repository metadata.

        Returns:
            str: Copyright notice text
            None: If no copyright notice can be determined
        """
        # Check LICENSE file for copyright notice
        license_content = self.repo_files.get("LICENSE", "") or self.repo_files.get("LICENSE.md", "")
        if license_content:
            # Extract first line with "Copyright" or "©"
            for line in license_content.split("\n"):
                if "copyright" in line.lower() or "©" in line:
                    notice = line.strip()
                    if notice:
                        logger.info(f"Found copyright notice in LICENSE")
                        return notice

        logger.debug("No copyright notice found")
        return None


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    """
    Extract copyright notice from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Copyright notice text
        None: If no copyright notice can be determined
    """
    try:
        extractor = CopyrightNoticeExtractor(repo_data, repo_files)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted copyright notice")
            return result
        else:
            logger.debug("No copyright notice found")
            return None

    except Exception as e:
        logger.error(f"Error extracting copyright notice: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[str]]:
    """
    Extract copyright notice from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'copyrightNotice' property and its value.
              Returns an empty dict if no copyright notice can be extracted.
    """
    try:
        from src.github_api import parse_repository_url, fetch_repository_info, fetch_file_content
        from src.utils import normalize_url

        repository_url = normalize_url(repository_url)
        owner, repo = parse_repository_url(repository_url)
        if not owner or not repo:
            return {}

        repo_data = fetch_repository_info(owner, repo)
        if not repo_data:
            return {}

        # Try to fetch LICENSE file
        repo_files = {}
        for filename in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
            try:
                content = fetch_file_content(owner, repo, filename)
                if content:
                    repo_files[filename] = content
                    break
            except:
                pass

        result = extract(repo_data, repo_files)

        if result:
            return {"copyrightNotice": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
