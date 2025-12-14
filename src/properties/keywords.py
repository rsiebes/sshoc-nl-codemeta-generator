"""
Keywords Property Module

Handles extraction and validation of the 'keywords' Codemeta property.
Keywords are tags or terms that describe the software for discoverability.
"""

from typing import Dict, Any, Optional, List, Union
from src.base_metadata import BaseMetadata


class KeywordsMetadata(BaseMetadata):
    """Handles keywords metadata extraction and validation."""

    CODEMETA_PROPERTY = 'keywords'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract keywords from raw data.

        Keywords can come from:
        1. Direct 'keywords' field (array or comma-separated string)
        2. 'topics' field (GitHub topics)
        3. 'tags' field
        4. 'subjects' field

        Returns:
            Dictionary with 'keywords' key containing array of keywords
        """
        keywords = []
        
        # Try to extract from different sources
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
        
        # Try subjects
        if not keywords:
            subjects = self._get_value('subjects')
            if subjects:
                keywords.extend(self._process_keywords(subjects))
        
        if not keywords:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(keyword)
        
        if unique_keywords:
            self.metadata[self.CODEMETA_PROPERTY] = unique_keywords
            return self.metadata
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' could not be processed")
            return {}

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
            # Convert to lowercase for consistency (optional)
            # keyword = keyword.lower()
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
