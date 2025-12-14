"""
BUILD instructions Module

Handles extraction and validation of the 'BUILD instructions' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class BuildInstructionsMetadata(BaseMetadata):
    """Handles BUILD instructions metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract BUILD instructions from raw data.

        Returns:
            Dictionary with 'build_instructions' key
        """
        value = self._get_value('build_instructions')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_url(value)
        
        if cleaned_value is not None:
            self.metadata['build_instructions'] = cleaned_value
        
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
        """Validate BUILD instructions metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('build_instructions')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'BUILD instructions' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'build_instructions': self.metadata['build_instructions']
        }
