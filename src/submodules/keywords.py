"""Submodule for extracting keywords from repository using Google Gemini API."""

from typing import Any, Dict, List, Optional

from src.core import get_logger
from src.helpers.gemini_extractor import extract_keywords
from src.submodules.base import BaseSubmodule

logger = get_logger(__name__)


class KeywordsSubmodule(BaseSubmodule):
    """Extract keywords from repository using Google Gemini API."""

    PROPERTY_NAME = "keywords"
    CATEGORY = "ai_extraction"

    def extract(self) -> Optional[List[str]]:
        """
        Extract keywords from repository using Gemini API.

        Returns:
            List of keyword strings (10 keywords), or None if extraction fails
        """
        try:
            # Get repository URL from repo_data
            repo_url = self.repo_data.get("data", {}).get("html_url")

            if not repo_url:
                logger.warning(
                    "Repository URL not found in repo_data, cannot extract keywords"
                )
                return None

            logger.debug(f"Extracting keywords for repository: {repo_url}")

            # Call Gemini extractor
            keyword_objects = extract_keywords(repo_url)

            if not keyword_objects:
                logger.warning(f"No keywords extracted for {repo_url}")
                return None

            # Extract only keyword names (not context_clues) for Codemeta output
            keyword_names = [keyword.name for keyword in keyword_objects]

            logger.info(
                f"Successfully extracted {len(keyword_names)} keywords for {repo_url}"
            )

            return keyword_names

        except Exception as e:
            self.error = str(e)
            logger.error(f"Error in KeywordsSubmodule.extract(): {self.error}")
            return None
