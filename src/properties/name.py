"""
Name Property Module

Handles extraction and validation of the 'name' Codemeta property.
The name is a required field that identifies the software.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class NameMetadata(BaseMetadata):
    """Handles name metadata extraction and validation."""

    CODEMETA_PROPERTY = 'name'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = True

    def extract(self) -> Dict[str, Any]:
        """
        Extract name from raw data.

        The name can come from:
        1. Direct 'name' field in raw data
        2. Repository name from GitHub
        3. Project name from README

        Returns:
            Dictionary with 'name' key
        """
        # Try different sources for the name
        name = self._get_value('name')
        
        if not name:
            # Try repository name as fallback
            name = self._get_value('repo_name')
        
        if not name:
            # Try project name from metadata
            name = self._get_value('project_name')

        if not name:
            self.add_error("Name could not be extracted from any source")
            return {}

        # Clean and validate the value
        cleaned_name = self._clean_string(name)
        
        if cleaned_name:
            self.metadata[self.CODEMETA_PROPERTY] = cleaned_name
            return self.metadata
        else:
            self.add_error("Name is empty or invalid")
            return {}

    def _validate_metadata(self) -> None:
        """Validate name metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        name = self.metadata.get(self.CODEMETA_PROPERTY)
        
        # Check if name exists
        if not name:
            self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Check if name is a string
        if not isinstance(name, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string, got {type(name).__name__}")
            return

        # Check minimum length
        if len(name) < 1:
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must not be empty")
            return

        # Check maximum length (reasonable limit)
        if len(name) > 500:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is very long ({len(name)} characters)")

        # Check for invalid characters
        if name.startswith(' ') or name.endswith(' '):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' has leading or trailing whitespace")

        # Check if name contains only whitespace
        if not name.strip():
            self.add_error(f"'{self.CODEMETA_PROPERTY}' contains only whitespace")

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

    def get_codemeta_type(self) -> str:
        """
        Get the Codemeta type for this property.

        Returns:
            Codemeta type string
        """
        return self.CODEMETA_TYPE

    def is_required(self) -> bool:
        """
        Check if this property is required.

        Returns:
            True if required, False otherwise
        """
        return self.REQUIRED
