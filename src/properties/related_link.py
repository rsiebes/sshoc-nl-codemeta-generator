"""
RELATED links Module

Handles extraction and validation of the 'RELATED links' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class RelatedLinkMetadata(BaseMetadata):
    """Handles RELATED links metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract RELATED links from raw data.

        Returns:
            Dictionary with 'related_link' key
        """
        value = self._get_value('related_link')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_list(value)
        
        if cleaned_value is not None:
            self.metadata['related_link'] = cleaned_value
        
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
        """Validate RELATED links metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('related_link')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'RELATED links' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'related_link': self.metadata['related_link']
        }
