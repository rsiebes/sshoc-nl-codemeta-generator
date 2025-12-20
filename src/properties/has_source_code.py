"""
Has Source Code Property Module

Handles extraction and validation of the 'has_source_code' Codemeta property.
Source code URL
"""

from typing import Dict, Any, Optional, Union, List
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class HasSourceCodeMetadata(BaseMetadata):
    """Handles has_source_code metadata extraction and validation."""

    CODEMETA_PROPERTY = 'hSourceCode'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract has_source_code from raw data.

        Returns:
            Dictionary with 'hSourceCode' key containing the extracted value
        """
        # Try to extract from raw data
        value = self._get_value('hSourceCode')
        
        if not value:
            # Try alternative field names
            value = self._get_value('has_source_code')
        
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
        """Validate has_source_code metadata."""
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
