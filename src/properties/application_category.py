"""
Application Category Property Module

This module detects the applicationCategory property for software by querying
external vocabularies (Wikidata) to find the most specific software category.
"""

import re
import requests
from typing import Optional, Tuple
from src.base_metadata import BaseMetadata
from src.vocabulary_cache import get_vocabulary_cache


class ApplicationCategoryMetadata(BaseMetadata):
    """Detects applicationCategory using external vocabulary lookup (Wikidata)."""

    CODEMETA_PROPERTY = 'applicationCategory'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    def __init__(self, raw_data: dict):
        """
        Initialize the applicationCategory detector.

        Args:
            raw_data: Raw metadata extracted from GitHub repository
        """
        super().__init__(raw_data)
        self.wikidata_api = "https://www.wikidata.org/w/api.php"

    def extract(self) -> None:
        """
        Extract applicationCategory by querying Wikidata for the software type.
        Uses local caching to avoid repeated API calls.
        """
        # Get repository name and description
        repo_name = self._get_value('name') or ''
        description = self._get_value('description') or ''
        readme_content = self._get_value('readme_content') or ''

        if not repo_name:
            self.metadata = None
            return

        # Check cache first
        cache = get_vocabulary_cache()
        cached_category = cache.get_category(repo_name)
        if cached_category:
            self.metadata = cached_category
            return

        # Try to find the software on Wikidata
        category = self._query_wikidata(repo_name, description, readme_content)
        
        # Cache the result
        if category:
            cache.set_category(repo_name, category)
        
        self.metadata = category

    def _query_wikidata(self, repo_name: str, description: str, readme_content: str) -> Optional[str]:
        """
        Query Wikidata to find the software category.

        Args:
            repo_name: Repository name
            description: Repository description
            readme_content: README content

        Returns:
            Most specific software category, or None if not found
        """
        # Combine search terms from description and README
        search_terms = self._extract_search_terms(description, readme_content)

        # Try searching with different terms
        for term in [repo_name] + search_terms:
            if not term or len(term) < 2:
                continue

            try:
                # Search for the software on Wikidata
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': f'{term} software',
                    'srnamespace': 0,
                    'srlimit': 5,
                }

                response = requests.get(self.wikidata_api, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()

                if data.get('query', {}).get('search'):
                    # Get the first result's title
                    result_title = data['query']['search'][0]['title']

                    # Get the entity data and extract category
                    category = self._get_entity_category(result_title)
                    if category:
                        return category

            except Exception as e:
                print(f"Warning: Error querying Wikidata for '{term}': {e}")
                continue

        return None

    def _extract_search_terms(self, description: str, readme_content: str) -> list:
        """
        Extract key search terms from description and README.

        Args:
            description: Repository description
            readme_content: README content

        Returns:
            List of search terms
        """
        terms = []

        # Extract from description
        if description:
            # Get first few words
            words = description.split()[:5]
            terms.append(' '.join(words))

        # Extract from README first sentence
        if readme_content:
            # Find first sentence (up to period, exclamation, or question mark)
            match = re.search(r'([^.!?]*[.!?])', readme_content)
            if match:
                sentence = match.group(1).strip()
                words = sentence.split()[:5]
                terms.append(' '.join(words))

        return terms

    def _get_entity_category(self, entity_title: str) -> Optional[str]:
        """
        Get entity category from Wikidata.

        Args:
            entity_title: Entity title from Wikidata search

        Returns:
            Entity category/description, or None if not found
        """
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'titles': entity_title,
                'prop': 'extracts',
                'explaintext': True,
                'exintro': True,
            }

            response = requests.get(self.wikidata_api, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            if pages:
                page_data = list(pages.values())[0]
                extract = page_data.get('extract', '')

                # Get the first sentence from the extract
                if extract:
                    # Find first sentence
                    match = re.search(r'([^.!?]*[.!?])', extract)
                    if match:
                        first_sentence = match.group(1).strip()
                        # Clean up and return
                        return first_sentence

        except Exception as e:
            self.logger.debug(f"Error getting entity category for '{entity_title}': {e}")

        return None

    def _validate_metadata(self) -> None:
        """Validate the extracted applicationCategory."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
        elif not isinstance(self.metadata, str):
            self.add_error(f"Field '{self.CODEMETA_PROPERTY}' must be a string")
        elif len(self.metadata) > 500:
            self.add_warning(f"Field '{self.CODEMETA_PROPERTY}' is very long ({len(self.metadata)} characters)")

    def to_codemeta_dict(self) -> dict:
        """Convert to Codemeta format."""
        if self.metadata:
            return {self.CODEMETA_PROPERTY: self.metadata}
        return {}
