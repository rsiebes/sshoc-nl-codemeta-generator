"""
THE date the software was last modified Module

Handles extraction and validation of the 'THE date the software was last modified' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class DateModifiedMetadata(BaseMetadata):
    """Handles THE date the software was last modified metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract THE date the software was last modified from raw data.

        Returns:
            Dictionary with 'date_modified' key
        """
        value = self._get_value('date_modified')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_date(value)
        
        if cleaned_value is not None:
            self.metadata['date_modified'] = cleaned_value
        
        return self.metadata

    def _clean_date(self, value: Any) -> Optional[Any]:
        """
        Clean and validate date value.

        Args:
            value: Raw value to clean

        Returns:
            Cleaned value or None
        """
        # TODO: Implement type-specific cleaning logic
        return value

    def _validate_metadata(self) -> None:
        """Validate THE date the software was last modified metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('date_modified')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'THE date the software was last modified' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'date_modified': self.metadata['date_modified']
        }
