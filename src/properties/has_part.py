"""
Has Part Property Module

Handles extraction and validation of the 'has_part' Codemeta property.
Component(s) of the software
"""

from typing import Dict, Any, Optional, Union, List
from src.base_metadata import BaseMetadata


class HasPartMetadata(BaseMetadata):
    """Handles has_part metadata extraction and validation."""

    CODEMETA_PROPERTY = 'hPart'
    CODEMETA_TYPE = 'schema:ItemList'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract has_part from raw data.

        Returns:
            Dictionary with 'hPart' key containing the extracted value
        """
        # Try to extract from raw data
        value = self._get_value('hPart')
        
        if not value:
            # Try alternative field names
            value = self._get_value('has_part')
        
        if not value:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' could not be extracted")
            else:
                self.add_warning(f"Optional field '{self.CODEMETA_PROPERTY}' could not be extracted")
            return {}
        
        # Process the value
        processed_value = self._process_value(value)
        
        if processed_value is not None:
            self.metadata[self.CODEMETA_PROPERTY] = processed_value
            return self.metadata
        else:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' could not be processed")
            return {}

    def _process_value(self, value: Any) -> Optional[Any]:
        """
        Process and normalize the extracted value.

        Args:
            value: Raw value from data source

        Returns:
            Processed value or None
        """
        # TODO: Implement value processing logic
        # This is a placeholder - implement specific logic for this property
        return value

    def _validate_metadata(self) -> None:
        """Validate has_part metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        value = self.metadata.get(self.CODEMETA_PROPERTY)
        
        if not value:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return
        
        # TODO: Implement validation logic specific to this property type
        # This is a placeholder - implement specific validation

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
