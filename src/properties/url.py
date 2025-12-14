"""
URL Property Module

Handles extraction and validation of the 'url' Codemeta property.
The URL points to the software's website or homepage.
"""

from typing import Dict, Any, Optional
import re
from src.base_metadata import BaseMetadata


class UrlMetadata(BaseMetadata):
    """Handles URL metadata extraction and validation."""

    CODEMETA_PROPERTY = 'url'
    CODEMETA_TYPE = 'schema:URL'
    REQUIRED = False

    def extract(self) -> Dict[str, Any]:
        """
        Extract URL from raw data.

        The URL can come from:
        1. Direct 'url' field in raw data
        2. Homepage field from GitHub
        3. Website field from repository metadata
        4. Code repository URL as fallback

        Returns:
            Dictionary with 'url' key
        """
        # Try different sources for the URL
        url = self._get_value('url')
        
        if not url:
            # Try homepage
            url = self._get_value('homepage')
        
        if not url:
            # Try website
            url = self._get_value('website')
        
        if not url:
            # Try code repository as fallback
            url = self._get_value('code_repository')

        if not url:
            self.add_warning("URL could not be extracted from any source")
            return {}

        # Normalize the URL first (adds protocol if missing)
        normalized_url = self._normalize_url(url)
        
        # Validate the URL
        if not self._is_valid_url(normalized_url):
            self.add_error(f"Invalid URL format: {url}")
            return {}

        if normalized_url:
            self.metadata[self.CODEMETA_PROPERTY] = normalized_url
            return self.metadata
        else:
            self.add_error("URL could not be normalized")
            return {}

    def _normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize a URL.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL or None
        """
        if not url:
            return None
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        
        # Remove trailing slash for consistency
        if url.endswith('/') and not url.endswith('://'):
            url = url.rstrip('/')
        
        return url

    def _validate_metadata(self) -> None:
        """Validate URL metadata."""
        if not self.metadata:
            if self.REQUIRED:
                self.add_error(f"Required field '{self.CODEMETA_PROPERTY}' is missing")
            return

        url = self.metadata.get(self.CODEMETA_PROPERTY)
        
        # Check if URL exists
        if not url:
            if self.REQUIRED:
                self.add_error(f"'{self.CODEMETA_PROPERTY}' is empty")
            return

        # Check if URL is a string
        if not isinstance(url, str):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' must be a string, got {type(url).__name__}")
            return

        # Check URL format
        if not self._is_valid_url(url):
            self.add_error(f"'{self.CODEMETA_PROPERTY}' is not a valid URL: {url}")
            return

        # Check URL length
        if len(url) > 2048:
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' is very long ({len(url)} characters)")

        # Check for common issues
        if ' ' in url:
            self.add_error(f"'{self.CODEMETA_PROPERTY}' contains spaces")

        # Validate URL structure
        if not self._is_valid_url_structure(url):
            self.add_warning(f"'{self.CODEMETA_PROPERTY}' may have invalid structure")

    def _is_valid_url_structure(self, url: str) -> bool:
        """
        Check if URL has valid structure.

        Args:
            url: URL to check

        Returns:
            True if valid structure, False otherwise
        """
        # Basic URL structure validation
        url_pattern = r'^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]+$'
        return bool(re.match(url_pattern, url))

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
