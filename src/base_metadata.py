"""
Base Metadata Module

Provides the abstract base class for all metadata extraction modules.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseMetadata(ABC):
    """Abstract base class for all metadata modules."""

    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize the metadata module.

        Args:
            raw_data: Raw data from scraper
        """
        self.raw_data = raw_data
        self.metadata = {}
        self.errors = []
        self.warnings = []

    @abstractmethod
    def extract(self) -> Dict[str, Any]:
        """
        Extract metadata from raw data.

        Returns:
            Dictionary containing extracted metadata
        """
        pass

    def validate(self) -> bool:
        """
        Validate extracted metadata.

        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self._validate_metadata()
        return len(self.errors) == 0

    @abstractmethod
    def _validate_metadata(self) -> None:
        """
        Perform validation checks.
        Should populate self.errors and self.warnings.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.

        Returns:
            Dictionary representation of metadata
        """
        return self.metadata

    def to_codemeta_dict(self) -> Dict[str, Any]:
        """
        Convert to Codemeta format.

        Returns:
            Dictionary in Codemeta format
        """
        return self.to_dict()

    def get_errors(self) -> List[str]:
        """
        Get validation errors.

        Returns:
            List of error messages
        """
        return self.errors

    def get_warnings(self) -> List[str]:
        """
        Get validation warnings.

        Returns:
            List of warning messages
        """
        return self.warnings

    def add_error(self, message: str) -> None:
        """
        Add an error message.

        Args:
            message: Error message
        """
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """
        Add a warning message.

        Args:
            message: Warning message
        """
        self.warnings.append(message)

    def _get_value(self, key: str, default: Any = None) -> Any:
        """
        Safely get a value from raw data.

        Args:
            key: Key to retrieve
            default: Default value if key not found

        Returns:
            Value from raw data or default
        """
        return self.raw_data.get(key, default)

    def _get_nested_value(self, path: str, default: Any = None) -> Any:
        """
        Safely get a nested value from raw data.

        Args:
            path: Dot-separated path (e.g., 'owner.name')
            default: Default value if path not found

        Returns:
            Value from raw data or default
        """
        keys = path.split('.')
        value = self.raw_data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def _is_valid_url(self, url: Optional[str]) -> bool:
        """
        Check if a string is a valid URL.

        Args:
            url: URL string to validate

        Returns:
            True if valid URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        return url.startswith(('http://', 'https://', 'ftp://'))

    def _is_valid_email(self, email: Optional[str]) -> bool:
        """
        Check if a string is a valid email.

        Args:
            email: Email string to validate

        Returns:
            True if valid email, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return '@' in email and '.' in email.split('@')[1]

    def _is_valid_date(self, date_str: Optional[str]) -> bool:
        """
        Check if a string is a valid ISO 8601 date.

        Args:
            date_str: Date string to validate

        Returns:
            True if valid date, False otherwise
        """
        if not date_str or not isinstance(date_str, str):
            return False
        # Basic ISO 8601 validation
        return (
            len(date_str) >= 10 and
            date_str[4] == '-' and
            date_str[7] == '-'
        )

    def _normalize_list(self, value: Any) -> List[Any]:
        """
        Normalize a value to a list.

        Args:
            value: Value to normalize

        Returns:
            List containing the value(s)
        """
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str) and value:
            return [value]
        return []

    def _clean_string(self, value: Optional[str]) -> Optional[str]:
        """
        Clean a string value.

        Args:
            value: String to clean

        Returns:
            Cleaned string or None
        """
        if not value or not isinstance(value, str):
            return None
        return value.strip() or None
