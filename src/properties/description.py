"""
Description Property Module

Handles extraction and validation of the 'description' Codemeta property.
The description provides a detailed explanation of what the software does.
"""

from typing import Dict, Any, Optional
from src.base_metadata import BaseMetadata
from src.execution_profiler import profile


class DescriptionMetadata(BaseMetadata):
    """Handles description metadata extraction and validation."""

    CODEMETA_PROPERTY = 'description'
    CODEMETA_TYPE = 'schema:Text'
    REQUIRED = True

    def extract(self) -> Dict[str, Any]:
        """
        Extract description from raw data.

        The description can come from:
        1. Direct 'description' field in raw data
        2. Repository description from GitHub
        3. First paragraph of README

        Returns:
            Dictionary with 'description' key
        """
        # Try different sources for the description
        description = self._get_value('description')
        
        if not description:
            # Try from GitHub repository description
            description = self._get_value('repo_description')
        
        if not description:
            # Try from README (first non-header paragraph)
            readme = self._get_value('readme')
            if readme:
                # Extract first paragraph from README
                description = self._extract_first_paragraph(readme)

        if not description:
            self.add_error("Description could not be extracted from any source")
            return {}

        # Clean and validate the value
        cleaned_description = self._clean_string(description)
        
        if cleaned_description:
            self.metadata[self.CODEMETA_PROPERTY] = cleaned_description
            return self.metadata
        else:
            self.add_error("Description is empty or invalid")
            return {}

    def _extract_first_paragraph(self, text: str) -> Optional[str]:
        """
        Extract the first non-header paragraph from text.

        Args:
            text: Text to extract from

        Returns:
            First non-header paragraph or None
        """
        if not text:
            return None
        
        # Split by double newline to get paragraphs
        paragraphs = text.split('\n\n')
        if not paragraphs:
            return None
        
        # Find first non-header paragraph
        for para in paragraphs:
            para = para.strip()
            if para:
                # Check if this paragraph starts with markdown header
                if para.startswith('#'):
                    # Remove headers and continue
                    continue
                # Return first non-header paragraph
                return para
        
        return None

    def _validate_metadata(self) -> None:
        """Validate description metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        description = self.metadata.get(self.CODEMETA_PROPERTY)
        
        # Check if description exists
        if not description:
            self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Check if description is a string
        if not isinstance(description, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string, got {type(description).__name__}")
            return

        # Check minimum length
        if len(description) < 10:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is very short ({len(description)} characters)")

        # Check maximum length (reasonable limit)
        if len(description) > 5000:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is very long ({len(description)} characters)")

        # Check for invalid characters
        if description.startswith(' ') or description.endswith(' '):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' has leading or trailing whitespace")

        # Check if description contains only whitespace
        if not description.strip():
            self.add_error(f"'{self.CODEMETA_PROPERTY}' contains only whitespace")

        # Check for common placeholder text
        if any(placeholder in description.lower() for placeholder in ['todo', 'fixme', 'placeholder', 'example']):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' may contain placeholder text")

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
