"""
CodeMeta codeOfConduct Module

Extracts code of conduct information according to CodeMeta 3.1 standard.
The codeOfConduct property describes the code of conduct document for the project.

This module extracts code of conduct from:
1. CODE_OF_CONDUCT.md file
2. CONDUCT.md file
3. .github/CODE_OF_CONDUCT.md file
4. Repository topics mentioning code of conduct

Returns:
    str: URL to code of conduct document
    None: If no code of conduct can be determined
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CodeOfConductExtractor:
    """Extracts code of conduct from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any], repo_files: Dict[str, str] = None):
        """
        Initialize the CodeOfConductExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
            repo_files: Dictionary containing repository file contents
        """
        self.repo_data = repo_data
        self.repo_files = repo_files or {}
        self.repo_url = repo_data.get("html_url", "")

    def extract(self) -> Optional[str]:
        """
        Extract code of conduct information from repository metadata.

        Returns:
            str: URL to code of conduct document
            None: If no code of conduct can be determined
        """
        # Check for CODE_OF_CONDUCT.md file
        if "CODE_OF_CONDUCT.md" in self.repo_files:
            url = f"{self.repo_url}/blob/main/CODE_OF_CONDUCT.md"
            logger.info(f"Found CODE_OF_CONDUCT.md")
            return url

        # Check for CONDUCT.md file
        if "CONDUCT.md" in self.repo_files:
            url = f"{self.repo_url}/blob/main/CONDUCT.md"
            logger.info(f"Found CONDUCT.md")
            return url

        # Check for .github/CODE_OF_CONDUCT.md file
        if ".github/CODE_OF_CONDUCT.md" in self.repo_files:
            url = f"{self.repo_url}/blob/main/.github/CODE_OF_CONDUCT.md"
            logger.info(f"Found .github/CODE_OF_CONDUCT.md")
            return url

        logger.debug("No code of conduct file found")
        return None


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    """
    Extract code of conduct from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: URL to code of conduct document
        None: If no code of conduct can be determined
    """
    try:
        extractor = CodeOfConductExtractor(repo_data, repo_files)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted code of conduct URL")
            return result
        else:
            logger.debug("No code of conduct found")
            return None

    except Exception as e:
        logger.error(f"Error extracting code of conduct: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[str]]:
    """
    Extract code of conduct from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'codeOfConduct' property and its value.
              Returns an empty dict if no code of conduct can be extracted.
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

        # Try to fetch code of conduct files
        repo_files = {}
        for filename in ["CODE_OF_CONDUCT.md", "CONDUCT.md", ".github/CODE_OF_CONDUCT.md"]:
            try:
                content = fetch_file_content(owner, repo, filename)
                if content:
                    repo_files[filename] = content
            except:
                pass

        result = extract(repo_data, repo_files)

        if result:
            return {"codeOfConduct": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
