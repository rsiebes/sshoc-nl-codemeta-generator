"""
CodeMeta conformsTo Module

Extracts standards conformance information according to CodeMeta 3.1 standard.
The conformsTo property describes standards or specifications the software conforms to.

This module extracts conformance from:
1. Repository topics mentioning standards (REST, GraphQL, SPARQL, etc.)
2. README mentions of standards compliance
3. Repository description keywords

Returns:
    str: Single standard identifier
    list: Multiple standards if applicable
    None: If no conformance data can be determined
"""

import logging
import re
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)


class ConformsToExtractor:
    """Extracts standards conformance from GitHub repository metadata."""

    # Common standards and their identifiers
    STANDARDS = {
        "rest": "https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm",
        "graphql": "https://spec.graphql.org/",
        "sparql": "https://www.w3.org/TR/sparql11-query/",
        "rdf": "https://www.w3.org/RDF/",
        "owl": "https://www.w3.org/OWL/",
        "json-ld": "https://www.w3.org/TR/json-ld11/",
        "turtle": "https://www.w3.org/TR/turtle/",
        "openapi": "https://spec.openapis.org/",
        "swagger": "https://swagger.io/specification/",
        "json-schema": "https://json-schema.org/",
        "xml": "https://www.w3.org/XML/",
        "atom": "https://tools.ietf.org/html/rfc4287",
        "rss": "https://www.rssboard.org/rss-specification",
        "oai-pmh": "https://www.openarchives.org/pmh/",
        "dublin-core": "https://dublincore.org/",
        "skos": "https://www.w3.org/2004/02/skos/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "vcard": "https://www.w3.org/TR/vcard-rdf/",
        "oauth": "https://oauth.net/",
        "openid": "https://openid.net/",
        "saml": "https://en.wikipedia.org/wiki/SAML",
    }

    def __init__(self, repo_data: Dict[str, Any]):
        """
        Initialize the ConformsToExtractor.

        Args:
            repo_data: Dictionary containing repository metadata from GitHub API
        """
        self.repo_data = repo_data
        self.topics = repo_data.get("topics", []) or []
        self.description = repo_data.get("description", "")

    def extract(self) -> Optional[Union[str, List[str]]]:
        """
        Extract standards conformance from repository metadata.

        Returns:
            str: Single standard identifier
            list: Multiple standards if applicable
            None: If no conformance data can be determined
        """
        standards = []

        # Check topics for standards keywords
        for topic in self.topics:
            topic_lower = topic.lower()
            for standard_key, standard_url in self.STANDARDS.items():
                if standard_key in topic_lower:
                    if standard_url not in standards:
                        standards.append(standard_url)
                        logger.info(f"Found standard in topics: {standard_key}")

        # Check description for standards keywords
        description_lower = self.description.lower()
        for standard_key, standard_url in self.STANDARDS.items():
            if standard_key in description_lower:
                if standard_url not in standards:
                    standards.append(standard_url)
                    logger.info(f"Found standard in description: {standard_key}")

        if len(standards) == 0:
            logger.debug("No standards conformance found")
            return None
        elif len(standards) == 1:
            return standards[0]
        else:
            return standards


def extract(repo_data: Dict[str, Any], repo_files: Dict[str, str] = None, **kwargs) -> Optional[Union[str, List[str]]]:
    """
    Extract standards conformance from repository metadata.

    Args:
        repo_data: Dictionary containing repository metadata from GitHub API
        repo_files: Dictionary containing repository file contents (optional)
        **kwargs: Additional arguments (ignored)

    Returns:
        str: Single standard identifier
        list: Multiple standards if applicable
        None: If no conformance data can be determined
    """
    try:
        extractor = ConformsToExtractor(repo_data)
        result = extractor.extract()

        if result:
            logger.info(f"Extracted standards conformance")
            return result
        else:
            logger.debug("No standards conformance found")
            return None

    except Exception as e:
        logger.error(f"Error extracting standards conformance: {str(e)}")
        return None


def get(repository_url: str) -> Dict[str, Optional[Union[str, List[str]]]]:
    """
    Extract standards conformance from a GitHub repository.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        Dict: A dictionary containing the 'conformsTo' property and its value.
              Returns an empty dict if no conformance can be extracted.
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
            return {"conformsTo": result}
        else:
            return {}

    except Exception as e:
        logger.error(f"Error in get function: {str(e)}")
        return {}
