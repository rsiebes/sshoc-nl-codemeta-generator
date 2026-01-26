"""Author submodule for extracting author metadata using Gemini."""

from typing import Any, Dict, Optional

from src.core import get_logger
from src.helpers.gemini_author_extractor import extract_authors
from src.submodules.base import BaseSubmodule

logger = get_logger(__name__)


class AuthorSubmodule(BaseSubmodule):
    """Submodule for extracting author metadata from GitHub repositories."""

    PROPERTY_NAME = "author"
    CATEGORY = "ai_extraction"

    def extract(self) -> Optional[Dict[str, Any]]:
        """
        Extract author metadata from the repository using Gemini.

        Returns:
            Dictionary containing author metadata in CodeMeta 3.1 JSON-LD format, or None if extraction fails
        """
        try:
            # Extract repository URL from repo_data
            repo_url = self.repo_data.get("data", {}).get("html_url")

            if not repo_url:
                logger.warning(
                    "Repository URL not found in repo_data, cannot extract author metadata"
                )
                return None

            logger.info(f"AUTHOR SUBMODULE: repo_url = {repo_url}")
            logger.debug(f"Extracting author metadata for repository: {repo_url}")

            # Extract author metadata using Gemini
            author_data = extract_authors(repo_url)

            if author_data:
                logger.info(f"Successfully extracted author metadata for {repo_url}")
                return author_data
            else:
                logger.debug(f"No author metadata found for {repo_url}")
                return None

        except Exception as e:
            logger.error(f"Error in author extraction: {str(e)}")
            return None
