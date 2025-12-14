"""
Keywords Property Module

Handles extraction and validation of the 'keywords' Codemeta property.
Keywords are tags or terms that describe the software for discoverability.

This module uses NLP techniques to extract meaningful keywords from repository
content including description, README, and existing topics.
"""

from typing import Dict, Any, Optional, List, Union
from src.base_metadata import BaseMetadata
from src.nlp_utils import KeywordExtractor


class KeywordsMetadata(BaseMetadata):
    """Handles keywords metadata extraction and validation using NLP."""

    CODEMETA_PROPERTY = 'keywords'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize keywords metadata extractor.
        
        Args:
            raw_data: Raw repository data
        """
        super().__init__(raw_data)
        self.keyword_extractor = KeywordExtractor()

    def extract(self) -> Dict[str, Any]:
        """
        Extract keywords from raw data using NLP analysis.

        Keywords are extracted from:
        1. Repository description (high priority)
        2. README content (high priority)
        3. Existing topics/tags (medium priority)
        4. Repository name (low priority)

        Uses TF-IDF and frequency analysis to identify meaningful keywords.

        Returns:
            Dictionary with 'keywords' key containing array of keywords
        """
        # First try to get existing topics/keywords from metadata
        existing_keywords = self._get_existing_keywords()
        
        # Use NLP to extract keywords from repository content
        nlp_keywords = self.keyword_extractor.extract_from_repository_data(self.raw_data)
        
        # Combine existing and NLP-extracted keywords
        all_keywords = []
        
        # Add existing keywords first (they're explicitly set by maintainers)
        if existing_keywords:
            all_keywords.extend(existing_keywords)
        
        # Add NLP-extracted keywords
        if nlp_keywords:
            for keyword in nlp_keywords:
                # Avoid duplicates (case-insensitive)
                if keyword.lower() not in [k.lower() for k in all_keywords]:
                    all_keywords.append(keyword)
        
        if not all_keywords:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Limit to reasonable number of keywords
        final_keywords = all_keywords[:15]
        
        if final_keywords:
            self.metadata[self.CODEMETA_PROPERTY] = final_keywords
            return self.metadata
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' could not be processed")
            return {}

    def _get_existing_keywords(self) -> List[str]:
        """
        Get existing keywords from repository metadata.
        
        Returns:
            List of existing keywords
        """
        keywords = []
        
        # Try different sources for existing keywords
        raw_keywords = self._get_value('keywords')
        if raw_keywords:
            keywords.extend(self._process_keywords(raw_keywords))
        
        # Try topics (GitHub topics)
        if not keywords:
            topics = self._get_value('topics')
            if topics:
                keywords.extend(self._process_keywords(topics))
        
        # Try tags
        if not keywords:
            tags = self._get_value('tags')
            if tags:
                keywords.extend(self._process_keywords(tags))
        
        return keywords

    def _process_keywords(self, value: Any) -> List[str]:
        """
        Process and normalize keywords from various formats.

        Args:
            value: Raw keywords value (string, list, or other)

        Returns:
            List of normalized keyword strings
        """
        keywords = []
        
        if isinstance(value, str):
            # Handle comma-separated string
            if ',' in value:
                keywords = [k.strip() for k in value.split(',') if k.strip()]
            # Handle space-separated string
            elif ' ' in value and not any(sep in value for sep in [';', '|']):
                keywords = [k.strip() for k in value.split() if k.strip()]
            # Handle semicolon-separated string
            elif ';' in value:
                keywords = [k.strip() for k in value.split(';') if k.strip()]
            # Handle pipe-separated string
            elif '|' in value:
                keywords = [k.strip() for k in value.split('|') if k.strip()]
            # Single keyword
            else:
                keyword = value.strip()
                if keyword:
                    keywords = [keyword]
        
        elif isinstance(value, list):
            # Handle list of keywords
            for item in value:
                if isinstance(item, str):
                    keyword = item.strip()
                    if keyword:
                        keywords.append(keyword)
                elif isinstance(item, dict):
                    # Handle dict with 'name' or 'value' key
                    keyword = item.get('name') or item.get('value')
                    if keyword and isinstance(keyword, str):
                        keyword = keyword.strip()
                        if keyword:
                            keywords.append(keyword)
        
        # Normalize keywords
        normalized = []
        for keyword in keywords:
            # Remove extra whitespace
            keyword = ' '.join(keyword.split())
            if keyword and len(keyword) <= 100:  # Reasonable max length
                normalized.append(keyword)
        
        return normalized

    def _validate_metadata(self) -> None:
        """Validate keywords metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        keywords = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not keywords:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return
        
        # Validate that keywords is a list
        if not isinstance(keywords, list):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be an array, got {type(keywords).__name__}")
            return
        
        # Validate each keyword
        for i, keyword in enumerate(keywords):
            if not isinstance(keyword, str):
                self.add_error(f"Keyword {i+1} must be a string, got {type(keyword).__name__}")
            elif not keyword.strip():
                self.add_error(f"Keyword {i+1} is empty")
            elif len(keyword) > 100:
                self.add_warning(f"Keyword {i+1} is very long ({len(keyword)} characters)")
        
        # Check for reasonable number of keywords
        if len(keywords) > 50:
            self.add_warning(f"Large number of keywords ({len(keywords)}), consider reducing")
        elif len(keywords) == 0:
            self.add_warning("Keywords array is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            self.CODEMETA_PROPERTY: self.metadata[self.CODEMETA_PROPERTY]
        }
