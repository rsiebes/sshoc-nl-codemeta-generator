"""
KEYWORDS describing the software Module

Handles extraction and validation of the 'KEYWORDS describing the software' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class KeywordsMetadata(BaseMetadata):
    """Handles KEYWORDS describing the software metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract KEYWORDS describing the software from raw data.

        Returns:
            Dictionary with 'keywords' key
        """
        value = self._get_value('keywords')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_list(value)
        
        if cleaned_value is not None:
            self.metadata['keywords'] = cleaned_value
        
        return self.metadata

    def _clean_list(self, value: Any) -> Optional[Any]:
        """
        Clean and validate list value.

        Args:
            value: Raw value to clean

        Returns:
            Cleaned value or None
        """
        # TODO: Implement type-specific cleaning logic
        return value

    def _validate_metadata(self) -> None:
        """Validate KEYWORDS describing the software metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('keywords')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'KEYWORDS describing the software' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'keywords': self.metadata['keywords']
        }
