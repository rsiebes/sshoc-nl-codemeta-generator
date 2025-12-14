"""
THE programming language(s) used Module

Handles extraction and validation of the 'THE programming language(s) used' Codemeta property.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata


class ProgrammingLanguageMetadata(BaseMetadata):
    """Handles THE programming language(s) used metadata extraction and validation."""

    def extract(self) -> Dict[str, Any]:
        """
        Extract THE programming language(s) used from raw data.

        Returns:
            Dictionary with 'programming_language' key
        """
        value = self._get_value('programming_language')
        
        if value is None:
            return {}

        # Clean and validate the value
        cleaned_value = self._clean_list(value)
        
        if cleaned_value is not None:
            self.metadata['programming_language'] = cleaned_value
        
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
        """Validate THE programming language(s) used metadata."""
        if not self.metadata:
            return

        value = self.metadata.get('programming_language')
        
        # TODO: Add validation logic specific to this property
        # Examples:
        # - Check required fields
        # - Validate format
        # - Check constraints
        
        if value is None:
            self.add_warning("'THE programming language(s) used' is empty")

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        if not self.metadata:
            return {}
        
        return {
            'programming_language': self.metadata['programming_language']
        }
