"""
Keywords Property Module

Handles extraction and validation of the 'keywords' Codemeta property.
Keywords are tags or terms that describe the software for discoverability.

This module extracts keywords from repository content and enhances them with
Wikidata URLs for semantic linking. Keywords with dashes, underscores, or spaces
are treated as single phrases and never split into individual words.

Output format:
{
  "keywords": [
    {
      "@type": "DefinedTerm",
      "name": "machine-learning",
      "url": "https://www.wikidata.org/wiki/Q2539",
      "description": "Field of study in artificial intelligence"
    },
    ...
  ]
}
"""

from typing import Dict, Any, Optional, List, Union
from src.base_metadata import BaseMetadata
from src.nlp_utils import KeywordExtractor
from src.wikidata_keyword_resolver import WikidataKeywordResolver


class KeywordsMetadata(BaseMetadata):
    """Handles keywords metadata extraction with Wikidata semantic linking."""

    CODEMETA_PROPERTY = 'keywords'
    CODEMETA_TYPE = 'schema:DefinedTerm'
    REQUIRED = False

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize keywords metadata extractor.
        
        Args:
            raw_data: Raw repository data
        """
        super().__init__(raw_data)
        self.keyword_extractor = KeywordExtractor()
        self.wikidata_resolver = WikidataKeywordResolver()
        self.context = self._build_context()

    def _build_context(self) -> str:
        """
        Build context from repository data for disambiguation.

        Returns:
            String containing repository context
        """
        parts = []
        
        if self.raw_data.get('description'):
            parts.append(self.raw_data['description'])
        
        if self.raw_data.get('readme_content'):
            # Take first 500 chars of README
            readme = self.raw_data['readme_content'][:500]
            parts.append(readme)
        
        if self.raw_data.get('topics'):
            topics = self.raw_data.get('topics', [])
            if isinstance(topics, list):
                parts.extend(topics)
        
        return ' '.join(parts)

    def extract(self) -> Dict[str, Any]:
        """
        Extract keywords from raw data.

        Keywords are extracted from:
        1. Repository topics/tags (high priority - set by maintainers)
        2. NLP extraction from description and README (medium priority)

        Each keyword is preserved as-is (no splitting on dashes/underscores/spaces)
        and enhanced with Wikidata URL if a confident match is found.

        Returns:
            Dictionary with 'keywords' key containing array of keywords
        """
        # Get existing topics/keywords from metadata (highest priority)
        existing_keywords = self._get_existing_keywords()
        
        # Use NLP to extract additional keywords from repository content
        nlp_keywords = self.keyword_extractor.extract_from_repository_data(self.raw_data)
        
        # Combine keywords, avoiding duplicates
        all_keywords = []
        seen_lower = set()
        
        # Add existing keywords first (they're explicitly set by maintainers)
        for keyword in existing_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen_lower:
                all_keywords.append(keyword)
                seen_lower.add(keyword_lower)
        
        # Add NLP-extracted keywords
        for keyword in nlp_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen_lower:
                all_keywords.append(keyword)
                seen_lower.add(keyword_lower)
        
        if not all_keywords:
            self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Limit to reasonable number of keywords
        final_keywords = all_keywords[:15]
        
        # Enhance keywords with Wikidata information
        enhanced_keywords = []
        for keyword in final_keywords:
            enhanced = self._enhance_keyword(keyword)
            enhanced_keywords.append(enhanced)
        
        if enhanced_keywords:
            self.metadata[self.CODEMETA_PROPERTY] = enhanced_keywords
            return self.metadata
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' could not be processed")
            return {}

    def _enhance_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        Enhance a keyword with Wikidata information.
        
        The keyword is preserved as-is and never split. For example:
        - "machine-learning" is looked up as "machine learning" (normalized)
        - "bayesian_inference" is looked up as "bayesian inference" (normalized)
        - Never split into individual words like "machine" or "learning"

        Args:
            keyword: The keyword to enhance (preserved as-is)

        Returns:
            Dictionary with keyword and optional Wikidata reference
        """
        # Try to resolve keyword to Wikidata entity
        # The resolver will normalize separators but never split the term
        wikidata_info = self.wikidata_resolver.resolve_keyword(keyword, self.context)
        
        if wikidata_info:
            return {
                "@type": "DefinedTerm",
                "name": keyword,  # Preserve original format
                "url": wikidata_info['url'],
                "description": wikidata_info.get('description', '')
            }
        
        # Return keyword without Wikidata reference if resolution failed
        return {
            "@type": "DefinedTerm",
            "name": keyword
        }

    def _get_existing_keywords(self) -> List[str]:
        """
        Get existing keywords from repository metadata.
        
        Priority order:
        1. GitHub topics (highest - explicitly set by maintainers)
        2. Existing keywords field
        3. Tags
        
        Returns:
            List of existing keywords (combined from all sources, no duplicates)
        """
        keywords = []
        seen_lower = set()
        
        # HIGHEST PRIORITY: GitHub topics (like "geospatial", "balltree", "spatial-analysis")
        topics = self._get_value('topics')
        if topics:
            for kw in self._process_keywords(topics):
                kw_lower = kw.lower()
                if kw_lower not in seen_lower:
                    keywords.append(kw)
                    seen_lower.add(kw_lower)
        
        # MEDIUM PRIORITY: Existing keywords field
        raw_keywords = self._get_value('keywords')
        if raw_keywords:
            for kw in self._process_keywords(raw_keywords):
                kw_lower = kw.lower()
                if kw_lower not in seen_lower:
                    keywords.append(kw)
                    seen_lower.add(kw_lower)
        
        # LOW PRIORITY: Tags
        tags = self._get_value('tags')
        if tags:
            for kw in self._process_keywords(tags):
                kw_lower = kw.lower()
                if kw_lower not in seen_lower:
                    keywords.append(kw)
                    seen_lower.add(kw_lower)
        
        return keywords

    def _process_keywords(self, value: Any) -> List[str]:
        """
        Process and normalize keywords from various formats.
        
        IMPORTANT: This does NOT split keywords on dashes, underscores, or spaces.
        Keywords are preserved as-is from the source.

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
            # Handle semicolon-separated string
            elif ';' in value:
                keywords = [k.strip() for k in value.split(';') if k.strip()]
            # Handle pipe-separated string
            elif '|' in value:
                keywords = [k.strip() for k in value.split('|') if k.strip()]
            # Single keyword (may contain spaces, dashes, underscores)
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
        
        # Normalize keywords (remove extra whitespace, but preserve structure)
        normalized = []
        for keyword in keywords:
            # Remove extra whitespace within the keyword
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
            if isinstance(keyword, dict):
                # Check DefinedTerm structure
                if '@type' not in keyword or keyword['@type'] != 'DefinedTerm':
                    self.add_warning(f"Keyword {i+1} should have @type='DefinedTerm'")
                if 'name' not in keyword:
                    self.add_error(f"Keyword {i+1} must have 'name' field")
            elif isinstance(keyword, str):
                # Legacy string format
                if not keyword.strip():
                    self.add_error(f"Keyword {i+1} is empty")
                elif len(keyword) > 100:
                    self.add_warning(f"Keyword {i+1} is very long ({len(keyword)} characters)")
            else:
                self.add_error(f"Keyword {i+1} must be string or DefinedTerm object, got {type(keyword).__name__}")
        
        # Check for reasonable number of keywords
        if len(keywords) > 50:
            self.add_warning(f"Large number of keywords ({len(keywords)}), consider reducing")
        elif len(keywords) == 0:
            self.add_warning("Keywords array is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format with DefinedTerm objects.

        Returns:
            Dictionary in Codemeta format with keywords as DefinedTerm objects
        """
        if not self.metadata:
            return {}
        
        return {
            self.CODEMETA_PROPERTY: self.metadata[self.CODEMETA_PROPERTY]
        }
