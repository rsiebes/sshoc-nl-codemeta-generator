"""
THE URL of the software's website Module

Handles extraction and validation of the 'THE URL of the software's website' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class UrlMetadata(BaseMetadata):
    """Handles THE URL of the software's website metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract THE URL of the software's website from raw data.

        Returns:
            Dictionary with 'url' key
        """
        value = self._get_value('url')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_url(value)
        
        if cleaned_value is not None:
            self.metadata['url'] = cleaned_value
        
        return self.metadata

    def _clean_url(self, value: Any) -> Optional[Any]:
        """
        Clean and validate url value.

        Args:
            value: Raw value to clean

        Returns:
            Cleaned value or None
        """
        # TODO: Implement type-specific cleaning logic
        return value

    def _validate_metadata(self) -> None:
        """Validate THE URL of the software's website metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('url')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'THE URL of the software's website' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'url': self.metadata['url']
        }
