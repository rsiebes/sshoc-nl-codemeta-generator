"""
Application Category Property Module

This module detects the applicationCategory property for software by using:
1. Curated vocabulary of popular modern software (first priority)
2. Pre-built Wikidata vocabulary (fallback)
3. Local cache for previously found categories

Returns both the category label and the Wikidata/reference URL for semantic linking.
"""

import re
from typing import Optional, Dict, Any
from src.base_metadata import BaseMetadata
from src.vocabulary_cache import get_vocabulary_cache
from src.wikidata_vocabulary_builder import WikidataVocabularyBuilder
from src.curated_software_vocabulary import find_in_curated_vocabulary


class ApplicationCategoryMetadata(BaseMetadata):
    """Detects applicationCategory using curated and Wikidata vocabularies."""

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
        self.vocab_builder = WikidataVocabularyBuilder()
        # Store both the category metadata and the URL separately
        self.category_metadata = None

    def extract(self) -> None:
        """
        Extract applicationCategory by searching vocabularies in priority order:
        1. Curated vocabulary (modern software)
        2. Wikidata vocabulary (well-known software)
        3. Cache (previously found categories)
        
        Stores both the category label and reference URL.
        """
        # Get repository name and description
        repo_name = self._get_value('name') or ''
        description = self._get_value('description') or ''
        readme_content = self._get_value('readme_content') or ''

        if not repo_name:
            self.metadata = None
            self.category_metadata = None
            return

        # Check cache first
        cache = get_vocabulary_cache()
        cached_category = cache.get_category(repo_name)
        if cached_category:
            self.metadata = cached_category
            # Try to get full metadata from vocabularies
            if isinstance(cached_category, str):
                match = find_in_curated_vocabulary(cached_category)
                if not match:
                    match = self.vocab_builder.find_matching_category(cached_category)
                if match:
                    self.category_metadata = match
            return

        # Try to find the software in the vocabularies
        category_metadata = self._find_category_from_vocabularies(
            repo_name, description, readme_content
        )
        
        if category_metadata:
            # Store the label as metadata (for backward compatibility)
            self.metadata = category_metadata.get('label', '')
            self.category_metadata = category_metadata
            
            # Cache the result
            cache.set_category(repo_name, self.metadata)
        else:
            self.metadata = None
            self.category_metadata = None

    def _find_category_from_vocabularies(
        self, repo_name: str, description: str, readme_content: str
    ) -> Optional[Dict[str, str]]:
        """
        Find a matching category from curated and Wikidata vocabularies.
        Tries curated vocabulary first (modern software), then Wikidata.

        Args:
            repo_name: Repository name
            description: Repository description
            readme_content: README content

        Returns:
            Category metadata dict with label, description, url, qid; or None if not found
        """
        # Build search terms from description and README
        search_terms = self._extract_search_terms(description, readme_content)

        # Try searching with different terms
        for term in [repo_name] + search_terms:
            if not term or len(term) < 2:
                continue

            # Try curated vocabulary first (modern software)
            match = find_in_curated_vocabulary(term)
            if match:
                return match
            
            # Fall back to Wikidata vocabulary
            match = self.vocab_builder.find_matching_category(term)
            if match:
                return match

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
            
            # Also add individual important words
            important_words = [
                w for w in description.split()
                if len(w) > 4 and w.lower() not in [
                    'the', 'and', 'for', 'with', 'from', 'that', 'this'
                ]
            ]
            terms.extend(important_words[:3])

        # Extract from README first sentence
        if readme_content:
            # Find first sentence (up to period, exclamation, or question mark)
            match = re.search(r'([^.!?]*[.!?])', readme_content)
            if match:
                sentence = match.group(1).strip()
                words = sentence.split()[:5]
                terms.append(' '.join(words))

        return [t for t in terms if t and len(t) > 2]

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
        """
        Convert to Codemeta format.
        
        Returns both the category label and the reference URL if available.
        Includes QID for Wikidata entities.
        """
        if not self.metadata:
            return {}
        
        # Return the category label as the main property
        result = {self.CODEMETA_PROPERTY: self.metadata}
        
        # If we have full metadata with URL, add it as additional properties
        if self.category_metadata:
            if 'url' in self.category_metadata:
                result['applicationCategoryUrl'] = self.category_metadata['url']
            if 'qid' in self.category_metadata:
                result['applicationCategoryQID'] = self.category_metadata['qid']
            if 'description' in self.category_metadata and self.category_metadata['description']:
                result['applicationCategoryDescription'] = self.category_metadata['description']
        
        return result
