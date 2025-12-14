"""
THE author(s) of the software Module

Handles extraction and validation of the 'THE author(s) of the software' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class AuthorMetadata(BaseMetadata):
    """Handles THE author(s) of the software metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract THE author(s) of the software from raw data.

        Returns:
            Dictionary with 'author' key
        """
        value = self._get_value('author')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_list(value)
        
        if cleaned_value is not None:
            self.metadata['author'] = cleaned_value
        
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
        """Validate THE author(s) of the software metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('author')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'THE author(s) of the software' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'author': self.metadata['author']
        }
