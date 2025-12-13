"""
CodeMeta abstract Module

Extracts the abstract/summary of the software according to CodeMeta 3.1 standard.
The abstract property provides a brief summary or overview of what the software does.

This module extracts the abstract from:
1. Repository description (primary source)
2. README file (if description is too short)
3. GitHub API description field

Returns:
    str: Abstract/summary text
    None: If no abstract can be determined
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AbstractExtractor:
    """Extracts abstract from GitHub repository metadata."""

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the AbstractExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.description = repo_data.get("description", "")

    def extract(self) -> Optional[str]:
        """
        Extract abstract from repository metadata.

        Returns:
            str: Abstract text (repository description)
            None: If no abstract can be determined
        """
        # Use repository description as abstract
        if self.description and len(self.description.strip()) > 0:
            abstract = self.description.strip()
            
            # Ensure it's not too long (abstracts should be concise)
            # CodeMeta doesn't specify a max length, but abstracts are typically < 500 chars
            if len(abstract) <= 1000:
                logger.info(f"Extracted abstract: {abstract[:100]}...")
                return abstract
            else:
                # If description is too long, truncate to first sentence or 500 chars
                sentences = abstract.split('. ')
                if len(sentences) > 0:
                    first_sentence = sentences[0] + ('.' if not sentences[0].endswith('.') else '')
                    if len(first_sentence) <= 500:
                        logger.info(f"Extracted abstract (first sentence): {first_sentence[:100]}...")
                        return first_sentence
                
                # Fallback: truncate at 500 chars
                truncated = abstract[:500].rsplit(' ', 1)[0] + '...'
                logger.info(f"Extracted abstract (truncated): {truncated[:100]}...")
                return truncated

        logger.debug("No abstract found")
        return None


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[str]:
    """
    Extract abstract from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Abstract text
        None: If no abstract can be determined
    """
    try:
        extractor = AbstractExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted abstract: {result[:100]}...")
            return result
        else:
            logger.debug("No abstract found with sufficient data")
            return None

    except Exception as e:
        logger.error(f"Error extracting abstract: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[str]]:
    """
    Extract abstract from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'abstract' property and its value.
              Returns an empty dict if no abstract can be extracted.
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
            return {"abstract": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
