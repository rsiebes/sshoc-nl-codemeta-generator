"""
THE operating system(s) the software runs on Module

Handles extraction and validation of the 'THE operating system(s) the software runs on' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class OperatingSystemMetadata(BaseMetadata):
    """Handles THE operating system(s) the software runs on metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract THE operating system(s) the software runs on from raw data.

        Returns:
            Dictionary with 'operating_system' key
        """
        value = self._get_value('operating_system')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_list(value)
        
        if cleaned_value is not None:
            self.metadata['operating_system'] = cleaned_value
        
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
        """Validate THE operating system(s) the software runs on metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('operating_system')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'THE operating system(s) the software runs on' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'operating_system': self.metadata['operating_system']
        }
