"""
CodeMeta copyrightYear Module

Extracts copyright year information according to CodeMeta 3.1 standard.
The copyrightYear property describes the year(s) of copyright.

This module extracts copyright year from:
1. LICENSE file
2. Repository creation date
3. README file

Returns:
    str: Copyright year or year range (e.g., "2021" or "2021-2025")
    None: If no copyright year can be determined
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CopyrightYearExtractor:
    """Extracts copyright year from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any], repo_files: Dict[str, str] = None):
        """
        Initialize the CopyrightYearExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
            repo_files: Dictionary containing repository file contents
        """
        self.repo_data = repo_data
        self.repo_files = repo_files or {}
        self.created_at = repo_data.get("created_at", "")

    def extract(self) -> Optional[str]:
        """
        Extract copyright year from repository metadata.

        Returns:
            str: Copyright year or year range
            None: If no copyright year can be determined
        """
        # Check LICENSE file for copyright year
        license_content = self.repo_files.get("LICENSE", "") or self.repo_files.get("LICENSE.md", "")
        if license_content:
            # Look for year patterns in LICENSE
            year_pattern = r'(20\d{2}(?:\s*-\s*20\d{2})?)'
            matches = re.findall(year_pattern, license_content)
            if matches:
                year = matches[0].replace(" ", "")
                logger.info(f"Found copyright year in LICENSE: {year}")
                return year

        # Fallback to repository creation year
        if self.created_at:
            try:
                year = self.created_at[:4]
                logger.info(f"Using repository creation year: {year}")
                return year
            except:
                pass

        logger.debug("No copyright year found")
        return None


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    """
    Extract copyright year from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Copyright year or year range
        None: If no copyright year can be determined
    """
    try:
        extractor = CopyrightYearExtractor(repo_data, repo_files)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted copyright year")
            return result
        else:
            logger.debug("No copyright year found")
            return None

    except Exception as e:
        logger.error(f"Error extracting copyright year: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[str]]:
    """
    Extract copyright year from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'copyrightYear' property and its value.
              Returns an empty dict if no copyright year can be extracted.
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
            return {"copyrightYear": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
